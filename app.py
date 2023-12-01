from flask import Flask, session, redirect, url_for, render_template, request, flash, jsonify
import os
import json
import stripe
from twilio.rest import Client

# Set your Twilio credentials
twilio_account_sid = 'ACe990909ae89799958980653f744f3b2d'
twilio_auth_token = '4d7311b7d41cd118b8d645771ce1331e'
twilio_phone_number = 'whatsapp:+14155238886'
twilio_client = Client(twilio_account_sid, twilio_auth_token)

# Set your test secret key for Stripe
stripe.api_key = "sk_test_51OIS6hGfhJguOr7SCrwqtCPyCvnBCwwEcHsbv79JtwAJunR2Su6ji4GZx5jrGlULmvT0Ipx5g3pJjqI4uc3kDMfU00uPCuGOtm"

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# Hardcoded credentials
USERNAME = "vamshiroyal"
PASSWORD = "Royal@1999"


@app.route("/")
def start():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == USERNAME and password == PASSWORD:
        # Store the username in the session
        session['username'] = username

        # Generate and send OTP via Twilio WhatsApp
        otp_generated = generate_and_send_otp(username)

        if otp_generated:
            # Redirect to the MFA page
            return redirect(url_for('otp_verification'))
        else:
            flash("OTP could not be sent. Please try again.")
            return redirect(url_for('start'))

    else:
        flash("Login Failed")
        return redirect(url_for('start'))


# Function to generate and send OTP via Twilio WhatsApp
def generate_and_send_otp(username):
    try:
        # Generate a random OTP (you can use a library like `random` for this)
        import random
        otp = ''.join(random.choice('0123456789') for i in range(6))

        # Compose the OTP message
        otp_message = f"Your OTP for login to Grocery Store is: {otp}"

        # Replace with your Twilio WhatsApp number
        to_whatsapp_number = 'whatsapp:+19408435653'

        # Send the OTP message via Twilio
        twilio_client.messages.create(
            body=otp_message,
            from_=twilio_phone_number,
            to=to_whatsapp_number
        )

        # Store the OTP in the session for later verification
        session['otp'] = otp

        return True

    except Exception as e:
        print(f"Error sending OTP: {str(e)}")
        return False


@app.route('/otp_verification', methods=['GET', 'POST'])
def otp_verification():
    if 'username' not in session:
        return redirect(url_for('start'))

    error_message = ''  # Initialize error_message to None

    if request.method == 'POST':
        user_input_otp = request.form['otp']
        stored_otp = session.get('otp')

        if user_input_otp == stored_otp:
            # OTP verification successful, remove stored OTP from session
            session.pop('otp', None)
            return redirect(url_for('home'))  # Redirect to home.html after successful OTP verification

        else:
            error_message = "OTP verification failed. Please try again."

    return render_template('mfa.html', error_message=error_message)  # Pass error_message to the template


@app.route('/resend_otp', methods=['POST'])
def resend_otp():
    if 'username' not in session:
        return redirect(url_for('start'))

    # Generate and send OTP via Twilio WhatsApp
    otp_generated = generate_and_send_otp(session['username'])

    if otp_generated:
        flash("OTP has been resent.")
    else:
        flash("OTP could not be resent. Please try again.")

    return redirect(url_for('otp_verification'))  # Redirect back to OTP verification page


@app.route('/home')
def home():
    items = get_product_items()  # This function call populates the items list
    return render_template('home.html', items=items)


def get_product_items():
    products_dir = os.path.join('static', 'items')
    products = []

    for item_name in os.listdir(products_dir):
        item_dir = os.path.join(products_dir, item_name)
        if os.path.isdir(item_dir):
            image_path = f"items/{item_name}/{item_name}_Iconic.jpg"
            description_path = os.path.join(item_dir, f"{item_name}_Description.txt")
            information_path = os.path.join(item_dir, f"{item_name}_Information.txt")
            price_path = os.path.join(item_dir, f"{item_name}_Price.txt")

            # Read the content of the description, information, and price files
            with open(description_path, 'r') as file:
                description = file.read().strip()
            with open(information_path, 'r') as file:
                information = file.read().strip()
            with open(price_path, 'r') as file:
                price = file.read().strip()

            # Append the product data to the products list
            products.append({
                'name': item_name.capitalize(),
                'image': image_path,
                'description': description,
                'information': information,
                'price': price
            })

    return products


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = []

    name = request.form.get('name')
    price = request.form.get('price')
    image = request.form.get('image')

    # Add the item to the cart
    session['cart'].append({'name': name, 'price': price, 'image': image})
    session.modified = True

    # Redirect to the cart page or back to the products page
    return redirect(url_for('show_cart'))  # or return redirect(url_for('home'))


@app.route('/cart')
def show_cart():
    # Display the cart items
    cart_items = session.get('cart', [])
    return render_template('cart.html', cart=cart_items)


@app.route('/checkout', methods=['POST'])
def checkout():
    if 'cart' not in session or not session['cart']:
        # If there is no cart or it's empty, redirect to the home or cart page
        return redirect(url_for('home'))

    # Calculate total items and total price
    total_items = sum(item.get('quantity', 1) for item in session['cart'])  # Default quantity to 1 if not present
    total_price = sum(item.get('quantity', 1) * float(item['price'].replace('$', '')) for item in session['cart'])

    # Render the checkout page with the cart items and totals
    return render_template('billing.html', cart=session['cart'], total_items=total_items, total_price=f"${total_price:.2f}")


# Define the route for processing the payment
@app.route('/process_payment', methods=['POST'])
def process_payment():
    if request.method == 'POST':
        # Calculate the total amount of the payment
        cart_items = session.get('cart', [])
        total_price = sum(item.get('quantity', 1) * float(item['price'].replace('$', '')) for item in cart_items)

        try:
            # Create a PaymentIntent
            payment_intent = stripe.PaymentIntent.create(
                amount=int(total_price * 100),  # Amount in cents
                currency='usd',
                payment_method_types=['card'],
                description='Payment for products',
                confirm=True,  # Confirm the PaymentIntent immediately
            )

            # Return the client secret to the frontend
            client_secret = payment_intent.client_secret

            # Redirect to a payment success page or return the client secret to the frontend
            return jsonify({'clientSecret': client_secret})

        except stripe.error.StripeError as e:
            # Handle any Stripe errors and return an error response
            return jsonify({'error': str(e)})

    # If the request method is not POST, return an error response
    return jsonify({'error': 'Invalid request method'})


@app.route('/payment_completed')
def payment_completed():
    # Payment was successful.
    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')
    # Execute the payment...
    # Redirect to order confirmation page...
    return redirect(url_for('order_confirmation'))


@app.route('/payment_canceled')
def payment_canceled():
    # Handle the canceled payment...
    return redirect(url_for('cart'))


@app.route('/order_confirmation')
def order_confirmation():
    # Access the order details from the session or database
    order_details = session.get('order_details', {})
    # Clear the session cart if the order is completed
    session.pop('cart', None)
    session.pop('shipping_info', None)  # Clear shipping info if it's no longer needed
    # Render an order confirmation page
    return render_template('order_confirmation.html')


if __name__ == '__main__':
    app.run(debug=True)
