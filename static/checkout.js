document.addEventListener('DOMContentLoaded', function() {
    // Function to update the order summary on the checkout page
    function updateOrderSummary() {
        const orderItemsContainer = document.querySelector('.order-summary .order-items');
        const cart = JSON.parse(localStorage.getItem('cart')) || [];
        let totalItems = 0;
        let totalPrice = 0;

        // Clear existing items
        orderItemsContainer.innerHTML = '';

        // Add each cart item to the order summary
        cart.forEach(item => {
            totalItems += item.quantity;
            totalPrice += item.quantity * parseFloat(item.price.replace('$', ''));

            const itemElement = document.createElement('div');
            itemElement.className = 'order-item';
            itemElement.innerHTML = `
                <img src="${item.image}" alt="${item.name}">
                <p>${item.name} <span>${item.price}</span> <span>x${item.quantity}</span></p>
            `;
            orderItemsContainer.appendChild(itemElement);
        });

        // Update total items and price
        document.getElementById('total-items').textContent = totalItems;
        document.getElementById('total-price').textContent = `$${totalPrice.toFixed(2)}`;
    }

    // Call updateOrderSummary to initialize the order summary
    updateOrderSummary();

    // Handle shipping form submission
    const shippingForm = document.getElementById('shipping-form');
    shippingForm.addEventListener('submit', function(event) {
        event.preventDefault();
        // Here you would handle the form submission, for example:
        // 1. Collect all the form data
        const formData = new FormData(shippingForm);
        // 2. Send it to the server via an AJAX request (fetch, XMLHttpRequest, etc.)
        // 3. Handle the response from the server
    });

    // Event listener for back to cart button if needed
    const backToCartButton = document.querySelector('.back-to-cart-btn');
    backToCartButton.addEventListener('click', function(event) {
        event.preventDefault();
        window.location.href = '/cart'; // Adjust the URL as needed for your application
    });

    // Additional functionality as needed...
});
