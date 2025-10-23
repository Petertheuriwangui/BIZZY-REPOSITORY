document.getElementById("paymentForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    const phone_number = document.getElementById("phone_number").value;
    const amount = document.getElementById("amount").value;

    const responseDiv = document.getElementById("response");
    responseDiv.innerHTML = "Processing payment...";

    try {
        const response = await fetch("/stkpush", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ phone_number, amount })
        });

        const data = await response.json();
        responseDiv.innerHTML = JSON.stringify(data, null, 2);
    } catch (error) {
        responseDiv.innerHTML = "Error: " + error;
    }
});