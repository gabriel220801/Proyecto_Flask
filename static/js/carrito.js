document.addEventListener('DOMContentLoaded', function () {
    // Función para manejar clic en el botón "Eliminar"
    function eliminarProducto(event) {
        const productId = event.target.getAttribute('data-product-id');
    
        // Preguntar al usuario si desea eliminar el producto
        const confirmacion = confirm('¿Estás seguro de que deseas eliminar este producto del carrito?');
    
        if (confirmacion) {
            // Realizar la solicitud al servidor para eliminar el producto del carrito
            fetch(`/eliminar-del-carrito/${productId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error al eliminar el producto del carrito. Código: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.message) {
                    // Actualizar la interfaz o realizar otras acciones según tu lógica
                    alert('Producto eliminado del carrito exitosamente');
                    window.location.reload(); // Recargar la página para reflejar los cambios en el carrito
                } else {
                    console.error('Error al eliminar el producto del carrito:', data.error);
                }
            })
            .catch(error => {
                console.error('Error de red:', error);
            });
        }
    }

    // Función para manejar clic en el botón "Realizar Compra"
    function realizarCompra(event) {
        event.preventDefault();
    
        // Obtener la fecha actual
        const fechaActual = new Date().toLocaleDateString();
    
        // Obtener los productos seleccionados
        const productosSeleccionados = document.querySelectorAll('input[name="productos_seleccionados"]:checked');
        const productosNombres = [];
        let totalCompra = 0;
    
        productosSeleccionados.forEach((checkbox, index) => {
            const card = checkbox.closest('.card');
            const nombreProducto = card.querySelector('h4').innerText;
            const precioProducto = parseFloat(card.querySelector('p').innerText.replace('Precio: $', ''));
            const cantidadProducto = parseInt(card.querySelector('p:nth-child(3)').innerText.replace('Cantidad: ', ''), 10);
    
            totalCompra += precioProducto * cantidadProducto;
    
            productosNombres.push(`
                <tr>
                    <td>${index + 1}</td>
                    <td>${nombreProducto}</td>
                    <td>${cantidadProducto}</td>
                    <td>$${precioProducto.toFixed(2)}</td>
                    <td>$${(precioProducto * cantidadProducto).toFixed(2)}</td>
                </tr>
            `);
        });
    
        // Crear el contenido de la factura con estilos y detalles adicionales
        const facturaContenido = productosNombres.length > 0
            ? `
                <style>
                    body {
                        background-color: #e6e6e6; /* Fondo de color gris claro */
                        padding: 20px;
                        font-family: Arial, sans-serif;
                    }
    
                    .factura-container {
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #fff; /* Fondo de color blanco */
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }
    
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 20px;
                    }
    
                    th, td {
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }
    
                    th {
                        background-color: #f2f2f2;
                    }
    
                    h2, h3 {
                        color: #333;
                    }
    
                    .total {
                        font-weight: bold;
                    }
    
                    .tienda-info {
                        margin-bottom: 20px;
                    }
    
                    .gracias-mensaje {
                        background-color: #4CAF50; /* Fondo de color verde (puedes cambiarlo según tus preferencias) */
                        color: #fff;
                        padding: 10px;
                        border-radius: 8px;
                        text-align: center;
                        margin-bottom: 20px;
                    }
                </style>
                <div class="factura-container">
                    <div class="gracias-mensaje">
                        <h3>¡Gracias por tu compra en Barbershop!</h3>
                    </div>
                    <div class="tienda-info">
                        <h2>Barbershop</h2>
                        <p>Fecha de compra: ${fechaActual}</p>
                    </div>
                    <h2>Factura de Compra</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Producto</th>
                                <th>Cantidad</th>
                                <th>Precio Unitario</th>
                                <th>Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${productosNombres.join('')}
                        </tbody>
                    </table>
                    <p class="total">Total de la compra: $${totalCompra.toFixed(2)}</p>
                </div>
            `
            : 'No has seleccionado ningún producto para comprar';
    
        // Abrir una nueva ventana emergente con la factura
        const facturaVentana = window.open('', 'Factura', 'width=600,height=400');
        facturaVentana.document.write('<html><head><title>Factura de Compra</title></head><body>');
        facturaVentana.document.write(facturaContenido);
        facturaVentana.document.write('</body></html>');
    
        // Desmarcar los productos seleccionados
        productosSeleccionados.forEach(checkbox => {
            checkbox.checked = false;
        });
    
        // Realizar la solicitud al servidor para realizar la compra
        fetch('/realizar-compra', {
            method: 'POST',
            body: JSON.stringify({ productosIds }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            // ... (código posterior)
        })
        .catch(error => {
            console.error('Error de red:', error);
        });
    }
    

    // Función para manejar clic en el botón "Comprar Todo"
    function comprarTodo() {
        const checkboxes = document.querySelectorAll('input[name="productos_seleccionados"]');
        
        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
        });
    }

    // Agregar un escuchador de eventos a todos los botones "Eliminar"
    const eliminarBtns = document.querySelectorAll('.eliminar-btn');
    eliminarBtns.forEach(btn => {
        btn.addEventListener('click', eliminarProducto);
    });

    // Agregar un escuchador de eventos al botón "Realizar Compra"
    const realizarCompraBtn = document.querySelector('.realizar-compra-btn');
    realizarCompraBtn.addEventListener('click', realizarCompra);

    // Agregar un escuchador de eventos al botón "Comprar Todo"
    const comprarTodoBtn = document.querySelector('.comprar-todo-btn');
    comprarTodoBtn.addEventListener('click', comprarTodo);
});
