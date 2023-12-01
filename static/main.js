document.addEventListener('DOMContentLoaded', function() {
    // Function to update the total price for an item
    function updateItemTotal(itemElement) {
        const priceElement = itemElement.querySelector('.item-price');
        const quantityInput = itemElement.querySelector('.item-quantity');
        const totalElement = itemElement.querySelector('.item-total');

        const price = parseFloat(priceElement.textContent.replace('$', ''));
        const quantity = parseInt(quantityInput.value, 10);
        const total = price * quantity;

        totalElement.textContent = '$' + total.toFixed(2);
    }

    // Function to update the total number of items and the overall total
    function updateCartSummary() {
        const cartItems = document.querySelectorAll('.cart-item');
        let totalItems = 0;
        let overallTotal = 0;

        cartItems.forEach(function(itemElement) {
            const quantityInput = itemElement.querySelector('.item-quantity');
            const totalElement = itemElement.querySelector('.item-total');

            const quantity = parseInt(quantityInput.value, 10);
            const total = parseFloat(totalElement.textContent.replace('$', ''));

            totalItems += quantity;
            overallTotal += total;
        });

        // Update the DOM with the new totals
        document.getElementById('item-count').textContent = totalItems;
        document.getElementById('total-price').textContent = '$' + overallTotal.toFixed(2);
    }

    // Attach event listeners to quantity controls
    document.querySelectorAll('.decrease-quantity').forEach(function(button) {
        button.addEventListener('click', function() {
            const itemElement = this.closest('.cart-item');
            const quantityInput = itemElement.querySelector('.item-quantity');
            const quantity = parseInt(quantityInput.value, 10) - 1;

            quantityInput.value = Math.max(quantity, 1); // Prevent quantity from being less than 1
            updateItemTotal(itemElement);
            updateCartSummary();
        });
    });

    document.querySelectorAll('.increase-quantity').forEach(function(button) {
        button.addEventListener('click', function() {
            const itemElement = this.closest('.cart-item');
            const quantityInput = itemElement.querySelector('.item-quantity');
            const quantity = parseInt(quantityInput.value, 10) + 1;

            quantityInput.value = quantity;
            updateItemTotal(itemElement);
            updateCartSummary();
        });
    });

    // Update totals when the quantity input is changed manually
    document.querySelectorAll('.item-quantity').forEach(function(input) {
        input.addEventListener('change', function() {
            const itemElement = this.closest('.cart-item');
            updateItemTotal(itemElement);
            updateCartSummary();
        });
    });

    // Initial update of the cart summary
    updateCartSummary();
});
