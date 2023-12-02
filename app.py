from flask import Flask, session, redirect, url_for, render_template, request, flash, jsonify
import os
import json
import stripe
from twilio.rest import Client



app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session managementx``


# Set your Twilio credentials
twilio_account_sid = 'ACe990909ae89799958980653f744f3b2d'
twilio_auth_token = '53fbd43721f3f0898abb7d2983f3b22d'
twilio_phone_number = 'whatsapp:+14155238886'
twilio_client = Client(twilio_account_sid, twilio_auth_token)

# Set your test secret key for Stripe
stripe.api_key = "sk_test_51OIS6hGfhJguOr7SCrwqtCPyCvnBCwwEcHsbv79JtwAJunR2Su6ji4GZx5jrGlULmvT0Ipx5g3pJjqI4uc3kDMfU00uPCuGOtm"

# Dummy initial balance (you should fetch this from your database)
initial_balance = 1000

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
        # items = get_product_items()
        # return render_template('mfa.html', items=items)
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
 

@app.route('/home')
def home():
    items = get_product_items()  # This function call populates the items list
    return render_template('home.html', items=items)



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

@app.route('/checkout')
def checkout():
    if 'cart' not in session or not session['cart']:
        # If there is no cart or it's empty, redirect to the home or cart page
        return redirect(url_for('home'))

    # Calculate total items and total price
    total_items = sum(item.get('quantity', 1) for item in session['cart'])  # Default quantity to 1 if not present
    total_price = sum(item.get('quantity', 1) * float(item['price'].replace('$', '')) for item in session['cart'])

    # Render the checkout page with the cart items and totals
    return render_template('checkout.html', cart=session['cart'], total_items=total_items, total_price=f"${total_price:.2f}")

@app.route('/process_checkout', methods=['GET', 'POST'])
def process_checkout():
    if request.method == 'POST':
        # Extract form data
        shipping_info = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'zip_code': request.form.get('zip'),
            'country': request.form.get('country'),
        }
        
        
        # Here, instead of saving to session, you might want to save to a database
        session['shipping_info'] = shipping_info
        
        # Instead of redirecting to the order confirmation, redirect to payment function
        return redirect(url_for('create_payment'))

    # If method is GET, or if any other method is used, redirect to home page as fallback
    return redirect(url_for('home'))





@app.route('/create_payment')
def create_payment():
        # Calculate total items and total price
    total_items = sum(item.get('quantity', 1) for item in session['cart'])  # Default quantity to 1 if not present
    total_price = sum(item.get('quantity', 1) * float(item['price'].replace('$', '')) for item in session['cart'])
    return render_template('test.html', total_items=total_items, total_price=f"${total_price:.2f}")

@app.route('/charge', methods=['POST'])
def charge():
    try:
        amount = float(request.form['amount'])
        token = request.form['token']  # Retrieve the token from the form

        # Charge the customer using the token
        charge = stripe.Charge.create(
            amount=int(float(amount * 100)),  # Amount should be in cents
            currency='usd',
            source=token,
        )

        # Update the Stripe balance (this is just a simple example)
        global initial_balance
        initial_balance += amount

        # return jsonify({"message": "Payment successful", "balance": initial_balance})
        return redirect(url_for('payment_completed'))

    except Exception as e:
        return jsonify({"error": str(e)}), 400

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



# if __name__ == '__main__':
#     app.run(debug=True)
# import os
# import stripe
# from flask import Flask, render_template, request, jsonify

# app = Flask(__name__)

# # Set your Stripe API key
# stripe.api_key = "sk_test_51OIS6hGfhJguOr7SCrwqtCPyCvnBCwwEcHsbv79JtwAJunR2Su6ji4GZx5jrGlULmvT0Ipx5g3pJjqI4uc3kDMfU00uPCuGOtm"

# # Dummy initial balance (you should fetch this from your database)
# initial_balance = 1000

# @app.route('/test')
# def test():
#     return render_template('test.html')



if __name__ == '__main__':
    app.run()
