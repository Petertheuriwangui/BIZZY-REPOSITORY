from flask import Blueprint, render_template, request, jsonify, redirect, url_for,flash,current_app,session
from flask_login import login_required, current_user
from . import db
import json
from werkzeug.security import check_password_hash, generate_password_hash
from .models import User,Listing,Profile
from werkzeug.utils import secure_filename
import os
from sqlalchemy import or_, and_
import random

views = Blueprint('views', __name__)



@views.route('/', methods=['GET'])
@login_required
def home():
    page = request.args.get('page', 1, type=int)  # Get current page
    per_page = 10  # Number of listings per page

    listings = Listing.query.all()  # Fetch all listings
    random.shuffle(listings)  # Shuffle listings

    # Paginate the shuffled listings manually
    total_listings = len(listings)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_listings = listings[start:end]

    return render_template("home.html", user=current_user, listings=paginated_listings, page=page, total=total_listings, per_page=per_page)

  # Pass listings to template

@views.route('/display', methods=['GET', 'POST'])
@login_required
def display():
    # Get filters from query parameters
    search = request.args.get('search', '').strip()
    category = request.args.get('category')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    # Start building the query
    query = Listing.query

    if search:
        query = query.filter(
            Listing.title.ilike(f'%{search}%') | Listing.description.ilike(f'%{search}%')
        )

    if category:
        query = query.filter_by(category=category)

    if min_price is not None:
        query = query.filter(Listing.price >= min_price)

    if max_price is not None:
        query = query.filter(Listing.price <= max_price)

    # Final listing result
    listings = query.all()

    # All listings without filter (if needed for other display)
    all_listings = Listing.query.all()

    return render_template(
        "display.html",
        user=current_user,
        listings=listings,
        all_listings=all_listings,
        category=category
    )



####show details of listing
@views.route('/show/<int:listing_id>')
@login_required
def show(listing_id):
    listing = Listing.query.get_or_404(listing_id)  # Fetch the listing by ID
    return render_template("show.html", listing=listing, user=current_user)



@views.route('/onlogin', methods=['GET', 'POST'])
def onlogin():
  listings = Listing.query.all()
   
  return render_template("onlogin.html", user=current_user, listings=listings) 



###faq###########
@views.route('/faq', methods=['GET', 'POST'])
def faq():

        return render_template('faq.html', user=current_user)
    
    
 ######contact###########   
@views.route('/contacts', methods=['GET', 'POST'])
def contacts():

        return render_template('contacts.html', user=current_user)
    
 #####termsandcondition###############     
@views.route('/termsandcondition', methods=['GET', 'POST'])
def termsandcondition():

        return render_template('termsandcondition.html', user=current_user) 
    
######privacypolicy###############
@views.route('/privacypolicy', methods=['GET', 'POST'])
def privacypolicy():

        return render_template('privacypolicy.html', user=current_user)
    
 #####aboutus###############   
@views.route('/aboutus', methods=['GET', 'POST'])
def aboutus():

        return render_template('aboutus.html', user=current_user)

####mpesa##############
@views.route('/mpesa-payment')
@login_required
def mpesa_payment():
    return render_template('mpesa_payment.html', user=current_user)

from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from .models import Listing,Cart
import os

UPLOAD_FOLDER = 'static', 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views.route('/listing', methods=['GET', 'POST'])
@login_required
def listing():
    # Check if user has made a valid payment
    

    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        price = request.form.get('price')
        condition = request.form.get('condition')
        description = request.form.get('description')
        location = request.form.get('location')
        seller = request.form.get('seller')
        phone = request.form.get('phone')
        email = request.form.get('email')
        images = request.files.getlist('images')

        filenames = []
        for image in images:
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                filenames.append(filename)

        image_filenames = ','.join(filenames) if filenames else "default.png"

        try:
            new_listing = Listing(
                title=title,
                category=category,
                price=float(price),
                condition=condition,
                description=description,
                location=location,
                seller=seller,
                phone=phone,
                email=email,
                images=image_filenames,
                user_id=current_user.id
            )
            db.session.add(new_listing)
            db.session.commit()
            flash("Listing added successfully!", category='success')
        except IntegrityError:
            db.session.rollback()
            flash("A database error occurred. Please try again.", category='danger')

        return redirect(url_for('views.listing'))

    listings = Listing.query.all()
    return render_template('listing.html', user=current_user, listings=listings)



@views.route('/userposts')
@login_required
def user_posts():
    # Fetch all posts created by the logged-in user
    listings = Listing.query.filter_by(user_id=current_user.id).all()
    return render_template('userposts.html', user=current_user, listings=listings, listing=None)

@views.route('/userposts/<int:listing_id>')
@login_required
def userpost_detail(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    return render_template('userposts.html', user=current_user, listings=None, listing=listing)

@views.route('/delete_post/<int:listing_id>', methods=['POST'])
@login_required
def delete_post(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    # Debugging - Confirm correct post selection
    print(f"Attempting to delete Listing ID: {listing.id}, Title: {listing.title}")

    if listing.user_id != current_user.id:
        flash("Unauthorized action!", category="danger")
        return redirect(url_for('views.user_posts'))

    try:
        # First, delete cart items referencing this listing
        Cart.query.filter_by(listing_id=listing.id).delete()
        db.session.commit()

        # Check and delete images only if they are NOT used in other listings
        if listing.images:
            images = listing.images.split(',')
            for image in images:
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image.strip())

                # Check if any other listing is using this image
                other_listings = Listing.query.filter(Listing.images.like(f"%{image.strip()}%"), Listing.id != listing.id).first()
                
                if not other_listings and os.path.exists(image_path) and image.strip() != "default.png":
                    os.remove(image_path)  # Delete image file only if it's not used elsewhere

        # Now delete the listing
        db.session.delete(listing)
        db.session.commit()

        flash("Post deleted successfully!", category="success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting post: {e}", category="danger")

    return redirect(url_for('views.user_posts'))


@views.route('/cart')
@login_required
def cart():
    user_cart_items = (
        db.session.query(Cart, Listing)
        .join(Listing, Cart.listing_id == Listing.id)
        .filter(Cart.user_id == current_user.id)  # Fetch only the logged-in user's cart items
        .all()
    )
    
    return render_template("cart.html", cart_items=user_cart_items, user=current_user)





from flask import jsonify

from flask import flash, redirect, url_for

from flask import jsonify

@views.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    listing_id = request.form.get('listing_id')

    # Prevent duplicate entries
    existing_item = Cart.query.filter_by(user_id=current_user.id, listing_id=listing_id).first()
    if not existing_item:
        new_cart_item = Cart(user_id=current_user.id, listing_id=listing_id)
        db.session.add(new_cart_item)
        db.session.commit()
        category = "success"
        message = "Item added to cart!"
    else:
        category = "error"
        message = "Item already in cart!"

    return jsonify({"status": category, "message": message, "listing_id": listing_id})


 

@views.route('/remove_from_cart', methods=['POST'])
@login_required
def remove_from_cart():
    listing_id = request.form.get('listing_id')
    
    cart_item = Cart.query.filter_by(user_id=current_user.id, listing_id=listing_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()

    return redirect(url_for('views.cart'))

from flask import g

@views.context_processor
def cart_count_processor():
    if current_user.is_authenticated:
        cart_count = db.session.query(Cart).filter(Cart.user_id == current_user.id).count()
    else:
        cart_count = 0
    return dict(cart_count=cart_count)

@views.route('/cart_count', methods=['GET'])
@login_required
def cart_count():
    count = db.session.query(Cart).filter(Cart.user_id == current_user.id).count()
    return jsonify({"count": count})


    
    
    ###profile pic upload####


@views.route('/update_password', methods=['POST'])
@login_required
def update_password():
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    
    if not check_password_hash(current_user.password, old_password):
        flash('Old password is incorrect!', 'danger')
        return redirect(request.referrer)
    
    current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
    db.session.commit()
    
    flash('Password updated successfully!', 'success')
    return redirect(url_for('views.profile'))

@views.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(current_user.id)
    
    db.session.delete(user)
    db.session.commit()
    
    flash('Your account has been deleted.', 'danger')
    return redirect(url_for('login.html'))

@views.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile = Profile.query.filter_by(user_id=current_user.id).first()

    if not profile:
        if request.method == 'POST':
            email = request.form.get('email')
            phone = request.form.get('phone')

            if not email or not phone:
                flash('Email and phone are required to create a profile.', 'danger')
                return redirect(url_for('views.profile'))

            # Check if email is already in use
            existing_email = Profile.query.filter_by(email=email).first()
            if existing_email:
                flash('This email is already taken. Please use a different one.', 'danger')
                return redirect(url_for('views.profile'))

            try:
                profile = Profile(
                    user_id=current_user.id,
                    email=email,
                    phone=phone,
                    location=request.form.get('location')
                )
                db.session.add(profile)
                db.session.commit()
                flash('Profile created successfully!', 'success')
            except IntegrityError:
                db.session.rollback()
                flash('Error creating profile. This email may already be in use.', 'danger')

            return redirect(url_for('views.profile'))

    elif request.method == 'POST':
        email = request.form.get('email')

        # Check if the new email is already used by another user
        existing_email = Profile.query.filter_by(email=email).first()
        if existing_email and existing_email.user_id != current_user.id:
            flash('This email is already taken. Please use a different one.', 'danger')
            return redirect(url_for('views.profile'))

        try:
            profile.email = email
            profile.phone = request.form.get('phone')
            profile.location = request.form.get('location')

            if 'profile_image' in request.files:
                image_file = request.files['profile_image']
                if image_file.filename != '':
                    image_path = f"Bizzy/static/uploads/{current_user.username}_{image_file.filename}"
                    image_file.save(image_path)
                    profile.profile_image = image_path
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('Error updating profile. This email may already be in use.', 'danger')

        return redirect(url_for('views.profile'))

    return render_template('profile.html', profile=profile, user=current_user)

@views.route('/preview_category/<category>')
def preview_category(category):
    listings = Listing.query.filter_by(category=category).limit(6).all()

    def get_first_image(images):
        if images:
            return images.split(',')[0]  # Take the first if multiple
        return 'default.jpg'

    return jsonify({
        'items': [
            {
                'title': l.title,
                'description': l.description[:60] + "...",
                'price': l.price,
                'image_url': url_for('static', filename=f'uploads/{get_first_image(l.images)}')
            } for l in listings
        ]
    })

