from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name= db.Column(db.String(150))
    second_name= db.Column(db.String(150))
    images= db.relationship('Listing')
    profile = db.relationship('Profile', backref='user', uselist=False, cascade="all, delete-orphan")

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    
    # Profile details
    profile_image = db.Column(db.String(255), nullable=True)  # Path to the image file
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    location = db.Column(db.String(255), nullable=True)
    
    



class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    images = db.Column(db.String(255), nullable=True)  # Store image filenames (comma-separated if multiple)
    seller = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 
    
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id',ondelete="CASCADE"), nullable=False)

    # Relationships
    user = db.relationship('User', backref='cart_items')
    listing = db.relationship('Listing', backref='cart_listings')
    


class MpesaTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt_number = db.Column(db.String(20), unique=True, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    transaction_date = db.Column(db.String(20), nullable=False)

    def __init__(self, receipt_number, amount, phone_number, transaction_date):
        self.receipt_number = receipt_number
        self.amount = amount
        self.phone_number = phone_number
        self.transaction_date = transaction_date
