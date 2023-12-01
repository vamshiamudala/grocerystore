from flask import Flask, session, redirect, url_for, render_template, request
import os
import json
import stripe

# Set your test secret key
stripe.api_key = "sk_test_51OIOTZI24DTmlTzT1qAD4lHqUMMswULW4yWjmYkEBizvIJZq2LSzUkpEEtuFelzz8wnbsbZZrx4rixHLiPyu02J800umS9WUkc"


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session managementx``

# Hardcoded credentials
USERNAME = "vamshiroyal"
PASSWORD = "Royal@1999"

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == USERNAME and password == PASSWORD:
        return render_template('camera.html')

    else:
        return "Login Failed", 401



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
 

@app.route('/')
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
        # Process the shipping information here
        # For example, save to a database or prepare for payment processing
    #     # After processing, you might redirect to a confirmation page or payment page
    #     return redirect(url_for('order_confirmation'))

    # # If method is GET, display the checkout page
    # cart_items = session.get('cart', [])
    # return render_template('checkout.html', cart=cart_items)






@app.route('/create_payment', methods=['POST'])
def create_payment():
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
            return json.dumps({'clientSecret': payment_intent.client_secret})

        except stripe.error.StripeError as e:
            # Handle any Stripe errors and return an error response
            return json.dumps({'error': str(e)})

    # If method is not POST, return an error response
    return json.dumps({'error': 'Invalid request method'})


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
