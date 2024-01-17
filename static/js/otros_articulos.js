// Archivo: static/js/custom.js

document.addEventListener("DOMContentLoaded", function() {
    // Agregar al carrito
    document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();

            const productId = this.getAttribute('data-product-id');
            const productName = this.getAttribute('data-product-name');
            const productQuantityInput = document.getElementById('cantidadInput' + productId);
            const productQuantity = productQuantityInput.value;
            const cantidadDisponible = parseInt(productQuantityInput.getAttribute('max'));

            // Verificar que la cantidad no sea negativa y no supere la cantidad disponible
            if (productQuantity < 1) {
                alert('No se pueden agregar cantidades negativas');
                return;
            } else if (productQuantity > cantidadDisponible) {
                alert('La cantidad ingresada supera la cantidad disponible');
                return;
            }

            // Realizar una solicitud para agregar al carrito
            fetch('/agregar-al-carrito', {
                method: 'POST',
                body: new URLSearchParams({
                    'id_producto': productId,
                    'cantidad': productQuantity
                }),
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);

            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
});
