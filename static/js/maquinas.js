async function verificarProductoEnCarrito(productId) {
    try {
        const response = await fetch('/verificar-en-carrito', {
            method: 'POST',
            body: new URLSearchParams({
                'id_producto': productId
            }),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });

        const data = await response.json();
        return data.en_carrito;
    } catch (error) {
        console.error('Error al verificar producto en carrito:', error);
        return false;
    }
}

document.addEventListener("DOMContentLoaded", function() {
    // Agregar al carrito
    document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', async function(event) {
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

            // Verificar si el producto ya está en el carrito
            const enCarrito = await verificarProductoEnCarrito(productId);

            if (enCarrito) {
                alert('El producto ya está en el carrito. La cantidad se actualizará.');

                // Actualizar la cantidad del producto en el carrito
                try {
                    const agregarResponse = await fetch('/agregar-al-carrito', {
                        method: 'POST',
                        body: new URLSearchParams({
                            'id_producto': productId,
                            'cantidad': productQuantity
                        }),
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded'
                        }
                    });

                    const agregarData = await agregarResponse.json();

                    alert(agregarData.message);
                } catch (error) {
                    console.error('Error al agregar producto al carrito:', error);
                }
            } else {
                // Si el producto no está en el carrito, realizar la solicitud para agregarlo
                try {
                    const agregarResponse = await fetch('/agregar-al-carrito', {
                        method: 'POST',
                        body: new URLSearchParams({
                            'id_producto': productId,
                            'cantidad': productQuantity
                        }),
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded'
                        }
                    });

                    const agregarData = await agregarResponse.json();

                    alert(agregarData.message);
                } catch (error) {
                    console.error('Error al agregar producto al carrito:', error);
                }
            }
        });
    });
});