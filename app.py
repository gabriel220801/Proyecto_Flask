import mysql.connector
import logging
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
from flask_bcrypt import Bcrypt
from mysql.connector import Error
from flask_paginate import Pagination, get_page_args
from flask import jsonify
import os
from werkzeug.utils import secure_filename
from flask_mail import Mail
from flask_mail import Message
import pymysql

logging.basicConfig(filename="logs.log", format="%(levelname)s:%(name)s:%(message)s", level=logging.DEBUG)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/img'
app.secret_key = 'your_secret_key'  # Cambia esto a una clave secreta más segura
bcrypt = Bcrypt(app)

# Configuración de la conexión a la base de datos
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="BD_TiendaBarberia"
)

#correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jeisondaneiro@gmail.com'
app.config['MAIL_PASSWORD'] = 'qjqe dctp sgui bwdu'  # Reemplaza con tu contraseña de correo
app.config['MAIL_DEFAULT_SENDER'] = 'jeisondaneiro@gmail.com'

mail = Mail(app)
#fin correo

# User model
class User:
    def __init__(self, nombre, telefono, correo, contraseña, id=None):
        self.id = id
        self.nombre = nombre
        self.telefono = telefono
        self.correo = correo
        self.contraseña = contraseña

    def obtener_lista_usuarios(self):  # Agregué 'self' como primer parámetro
        try:
            cursor = db.cursor()
            cursor.execute("SELECT id, nombre, telefono, correo FROM users WHERE rol='usuario'")
            lista_usuarios = cursor.fetchall()
            cursor.close()
            return lista_usuarios
        except Error as e:
            print(f"Error al obtener la lista de usuarios: {str(e)}")
            return []
     

    def agregar_producto_al_carrito(self, id_producto, cantidad):
        try:
            if 'id' not in session:
                return {'error': 'Usuario no autenticado'}, 401

            id_usuario = session['id']

            cursor = db.cursor()

            # Verificar si el producto ya está en el carrito
            cursor.execute("SELECT cantidad FROM carrito WHERE id_usuario = %s AND id_producto = %s", (id_usuario, id_producto))
            resultado = cursor.fetchone()

            if resultado:
                # Si el producto ya está en el carrito, actualizar la cantidad
                nueva_cantidad = resultado[0] + int(cantidad)
                cursor.execute("UPDATE carrito SET cantidad = %s WHERE id_usuario = %s AND id_producto = %s",
                            (nueva_cantidad, id_usuario, id_producto))
                db.commit()
                cursor.close()

                return {'message': 'Cantidad del producto actualizada en el carrito'}
            else:
                # Si el producto no está en el carrito, agregarlo
                cursor.execute("SELECT nombre, precio, imagen FROM productos WHERE id = %s", (id_producto,))
                producto_info = cursor.fetchone()

                if not producto_info:
                    cursor.close()
                    return {'error': 'Producto no encontrado en la base de datos'}

                cursor.execute(
                    "INSERT INTO carrito (id_usuario, id_producto, cantidad) VALUES (%s, %s, %s)",
                    (id_usuario, id_producto, cantidad)
                )
                db.commit()
                cursor.close()

                return {
                    'message': 'Producto agregado al carrito exitosamente',
                    'producto': {
                        'nombre': producto_info[0],
                        'precio': float(producto_info[1]),
                        'imagen': producto_info[2]
                    }
                }

        except Error as e:
            print(f"Error inesperado al agregar producto al carrito: {str(e)}")
            return {'error': 'Error al agregar producto al carrito'}


    def obtener_carrito(self):
        try:
            if 'id' not in session:
                return None

            id_usuario = session['id']

            cursor = db.cursor()
            cursor.execute(
                "SELECT carrito.id_carrito, productos.nombre, productos.precio, productos.imagen, carrito.cantidad FROM carrito INNER JOIN productos ON carrito.id_producto = productos.id WHERE carrito.id_usuario = %s;",
                (id_usuario,)
            )

            carrito = cursor.fetchall()
            cursor.close()

            return carrito
        except Error as e:
            print(f"Error al obtener el carrito: {str(e)}")
            return None

    def send_welcome_email(correo, nombre):
        subject = 'Bienvenido a BarberShop Style'
        body = f'Hola {nombre},\n\nGracias por registrarte en BarberShop Style. ¡Bienvenido!\n\nAtentamente,\nBarberShop Style Team'

        msg = Message(subject=subject, recipients=[correo], body=body)
        mail.send(msg)

    def eliminar_producto_carrito(self, id_carrito):
        try:
            cursor = db.cursor()
            cursor.execute("DELETE FROM carrito WHERE id_carrito = %s AND id_usuario = %s", (id_carrito, self.id))
            db.commit()
            cursor.close()
            return {'message': 'Producto eliminado del carrito exitosamente'}
        except Error as e:
            print(f"Error inesperado al eliminar producto del carrito: {str(e)}")
            return {'error': 'Error al eliminar producto del carrito'}

    def comprar_todo(self):
        try:
            cursor = db.cursor()
            cursor.execute("DELETE FROM carrito WHERE id_usuario = %s", (self.id,))
            db.commit()
            cursor.close()
            return {'message': 'Compra exitosa. ¡Gracias por tu compra!'}
        except Error as e:
            print(f"Error inesperado al realizar la compra: {str(e)}")
            return {'error': 'Error al realizar la compra'}


#definicion de correo      
def send_welcome_email(correo, nombre):
        subject = 'Bienvenido a BarberShop Style'
        body = f'Hola {nombre},\n\nGracias por registrarte en BarberShop Style. ¡Bienvenido!\n\nAtentamente,\nBarberShop Style Team'

        msg = Message(subject=subject, recipients=[correo], body=body)
        mail.send(msg)
#fin deficion de correo   





#Routes
@app.route('/')
def home():
    success_message = request.args.get('success_message', None)
    return render_template('home.html', success_message=success_message)

@app.route('/verificar-en-carrito', methods=['POST'])
def verificar_en_carrito():
    try:
        id_producto = int(request.form.get('id_producto'))

        if 'id' not in session:
            return jsonify({'en_carrito': False})

        id_usuario = session['id']

        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM carrito WHERE id_usuario = %s AND id_producto = %s", (id_usuario, id_producto))
        count = cursor.fetchone()[0]
        cursor.close()

        return jsonify({'en_carrito': count > 0})

    except Exception as e:
        print(f"Error al verificar producto en carrito: {str(e)}")
        return jsonify({'en_carrito': False})


@app.route('/realizar-compra', methods=['POST'])
def realizar_compra():
    try:
        if 'id' not in session:
            return jsonify({'error': 'Usuario no autenticado'}), 401

        id_usuario = session['id']
        productos_ids = request.json.get('productosIds', [])

        # Lógica para procesar la compra utilizando los productos_ids
        # ...

        return jsonify({'message': 'Compra realizada exitosamente'})

    except Exception as e:
        return jsonify({'error': str(e)})


#----------------------------ERRORES--------------------------------------------

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route('/ruta_que_no_existe')
def ruta_que_no_existe():
    # Puedes redirigir a la página de inicio o a cualquier otra ruta
    return redirect(url_for('404.html'))

#-----------------------------------FIN ERRORES-----------------------------------------




#-------------------------------------LOGIN---------------------------------------------

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':

        try:
            db.ping(True)
            correo = request.form['txtCorreo']
            contraseña = request.form['txtPassword']

            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE correo=%s", (correo,))
            user = cursor.fetchone()
            cursor.close()

            if user and bcrypt.check_password_hash(user[4], contraseña):
                # Inicio de sesión exitoso
                session['id'] = user[0]  # Establecer el ID en la sesión
                session['correo'] = correo
                session['nombre'] = user[1]
                
                # Verificar el rol del usuario
                if user[5] == 'administrador':
                    # Redirigir al panel de administrador
                    return redirect(url_for('lista_productos'))
                
                else:
                    # Mensaje de éxito para mostrar en la interfaz de usuario
                    success_message = '¡Hola y Bienvenido, {}!'.format(user[1])
                    
                    # Redirige a la página home con el mensaje de éxito directamente en el contexto
                    return redirect(url_for('home', success_message=success_message))

            else:
                # Inicio de sesión fallido
                error_message = 'Inicio de sesión fallido. Verifica tus Datos.'
                return render_template('login.html', error_message=error_message)

        except Error as e:
            # Error al conectarse a la base de datos
            error_message = 'Error al conectar con la base de datos. Por favor, inténtalo de nuevo más tarde.'
            return render_template('login.html', error_message=error_message)

    return render_template('login.html')

#_------------------------------------------FIN LOGIN-----------------------------------------



#-------------------------------------------REGISTRO USUARIO-----------------------------------

@app.route('/crear-registro', methods=['GET', 'POST'])
def crear_registro():
    error_message = None

    if request.method == 'POST':
        try:
            # Verificar la conexión a la base de datos
            with db.cursor() as cursor:
                db.ping(True)

                # Obtener datos del formulario
                nombre = request.form['txtNombre']
                telefono = request.form['txtTelefono']
                correo = request.form['txtCorreo']
                contraseña = request.form['txtPassword']

                # Validar campos
                if not nombre or not telefono or not correo or not contraseña:
                    error_message = 'Todos los campos son obligatorios. Por favor, completa todos los campos.'
                elif len(contraseña) < 4:
                    error_message = 'La contraseña debe tener al menos 4 caracteres.'
                elif any(char.isdigit() for char in nombre):
                    error_message = 'El nombre no puede contener números.'
                # Puedes agregar más validaciones aquí según tus necesidades

                else:
                    hashed_contraseña = bcrypt.generate_password_hash(contraseña).decode('utf-8')

                    # Verificar si el correo ya está registrado
                    cursor.execute("SELECT * FROM users WHERE correo=%s", (correo,))
                    existing_user = cursor.fetchone()

                    if existing_user:
                        error_message = 'El correo ya está registrado. Por favor, inicia sesión.'
                    else:
                        # Insertar nuevo usuario en la base de datos con el rol 'usuario'
                        cursor.execute("INSERT INTO users (nombre, telefono, correo, contraseña, rol) VALUES (%s, %s, %s, %s, 'usuario')",
                                    (nombre, telefono, correo, hashed_contraseña))
                        db.commit()

                        #mensaje del correo
                        send_welcome_email(correo, nombre)

                        error_message = 'Registro exitoso. ¡Inicia sesión ahora!'

        except Error as e:
            # Error al conectarse a la base de datos
            error_message = 'Error al conectar con la base de datos. Por favor, inténtalo de nuevo más tarde.'

    return render_template('login.html', error_message=error_message)

#-----------------------------FIN REGISTRO-----------------------------------------------



#-----------------------------CERRAR SESION----------------------------------------------

@app.route('/logout')
def logout():
    # Verificar si el usuario está actualmente autenticado
    if 'correo' in session:
        # Eliminar la clave 'correo' de la sesión
        session.pop('correo', None)

        # Mensaje de éxito para mostrar al cerrar sesión
        success_message = '¡Hasta pronto!'
        
        # Redirige a la página home con el mensaje de éxito
        return redirect(url_for('home', success_message=success_message))

    # Redirigir al usuario de nuevo a la página de inicio si no estaba autenticado
    return redirect(url_for('home'))


#---------------------------------FIN LOGOUT-----------------------------------------------




#--------------------------------PRODUCTOS----------------------------------------------

@app.route('/productos')
def productos():
    return render_template('productos.html')

@app.route('/productos/maquinas')
def maquinas():
    # Obtener el número de página actual
    page = request.args.get('page', 1, type=int)

    # Definir la cantidad de productos por página
    products_per_page = 9

    # Realizar consulta a la base de datos para obtener productos de la categoría "Maquinas"
    cursor = db.cursor()
    cursor.execute("SELECT id, nombre, precio, descripcion, cantidad, imagen FROM productos WHERE id_cat = 1")
    productos = cursor.fetchall()
    cursor.close()

    productos = [(producto[0], producto[1], int(producto[2]), producto[3], producto[4], producto[5]) for producto in productos]

    # Calcular el índice de inicio y fin para los productos en la página actual
    start_index = (page - 1) * products_per_page
    end_index = start_index + products_per_page

    # Seleccionar los productos correspondientes a la página actual
    productos_pagina = productos[start_index:end_index]

    # Configurar la paginación
    pagination = Pagination(page=page, total=len(productos), per_page=products_per_page, css_framework='bootstrap4')

    return render_template('maquinas.html', productos=productos_pagina, pagination=pagination)
    

@app.route('/productos/secadores')
def secadores():

    # Obtener el número de página actual
    page = request.args.get('page', 1, type=int)

    # Definir la cantidad de productos por página
    products_per_page = 9

    # Realizar consulta a la base de datos para obtener productos de la categoría "Secadores"
    cursor = db.cursor()
    cursor.execute("SELECT id, nombre, precio, descripcion, cantidad, imagen FROM productos WHERE id_cat = 2")
    productos = cursor.fetchall()
    cursor.close()

    productos = [(producto[0], producto[1], int(producto[2]), producto[3], producto[4], producto[5]) for producto in productos]

    # Calcular el índice de inicio y fin para los productos en la página actual
    start_index = (page - 1) * products_per_page
    end_index = start_index + products_per_page

    # Seleccionar los productos correspondientes a la página actual
    productos_pagina = productos[start_index:end_index]

    # Configurar la paginación
    pagination = Pagination(page=page, total=len(productos), per_page=products_per_page, css_framework='bootstrap4')

    return render_template('secadores.html', productos=productos_pagina, pagination=pagination)


@app.route('/productos/otros_articulos')
def otros_articulos():

    # Obtener el número de página actual
    page = request.args.get('page', 1, type=int)

    # Definir la cantidad de productos por página
    products_per_page = 9

    # Realizar consulta a la base de datos para obtener productos de la categoría "Otros_Articulos"
    cursor = db.cursor()
    cursor.execute("SELECT id, nombre, precio, descripcion, cantidad, imagen FROM productos WHERE id_cat = 3")
    productos = cursor.fetchall()
    cursor.close()

    productos = [(producto[0], producto[1], int(producto[2]), producto[3], producto[4], producto[5]) for producto in productos]

    # Calcular el índice de inicio y fin para los productos en la página actual
    start_index = (page - 1) * products_per_page
    end_index = start_index + products_per_page

    # Seleccionar los productos correspondientes a la página actual
    productos_pagina = productos[start_index:end_index]

    # Configurar la paginación
    pagination = Pagination(page=page, total=len(productos), per_page=products_per_page, css_framework='bootstrap4')

    return render_template('otros_articulos.html', productos=productos_pagina, pagination=pagination)



#----------------------------------FIN PRODUCTOS------------------------------------------





#---------------------------------------NOSOTROS-------------------------------------------

@app.route('/acercade')
def acercade():
    return render_template ('acercade.html')

#------------------------------------FIN NOSOTROS------------------------------------------





#-------------------------------------ADMIN------------------------------------------------
def obtener_cantidad_productos_por_categoria():
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT id_cat, COUNT(*) as cantidad FROM productos GROUP BY id_cat")
            results = cursor.fetchall()

            cantidad_por_categoria = {1: 0, 2: 0, 3: 0}

            for row in results:
                categoria_id, cantidad = row
                cantidad_por_categoria[categoria_id] = cantidad

            print("Cantidad por categoría:", cantidad_por_categoria)  # Agrega esta línea para imprimir

            return cantidad_por_categoria[1], cantidad_por_categoria[2], cantidad_por_categoria[3]

    except Error as e:
        print(f"Error al obtener la cantidad de productos por categoría: {str(e)}")
        return 0, 0, 0


@app.route('/admin')
def lista_productos():
    # Obtener cantidad de productos por categoría
    cantidad_secadores, cantidad_maquinas, cantidad_otros = obtener_cantidad_productos_por_categoria()

    # Renderizar la plantilla con las cantidades
    return render_template('admin.html', cantidades={
        'secadores': cantidad_maquinas,
        'maquinas': cantidad_secadores,
        'otros': cantidad_otros
    })






@app.route('/users')
def admin():
    # Crear una instancia de User
    user = User(nombre='', telefono='', correo='', contraseña='')
    lista_usuarios = user.obtener_lista_usuarios()
    return render_template('users_admin.html', lista_usuarios=lista_usuarios)

@app.route('/admin/productos-maquinas')
def productos_maquinas_admin():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id, nombre, precio, descripcion, cantidad, imagen FROM productos WHERE id_cat = 1")
        productos_maquinas = cursor.fetchall()
        cursor.close()

        # Pasa la lista de productos de máquinas a la plantilla
        return render_template('maquinas_admin.html', lista_productos=productos_maquinas)

    except Error as e:
        print(f"Error al obtener productos de máquinas: {str(e)}")
        # Manejo del error, redirigir o mostrar un mensaje de error según sea necesario
        return render_template('maquinas_admin.html', error_message='Error al obtener productos de máquinas')
    

@app.route('/admin/productos-secadores')
def productos_secadores_admin():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id, nombre, precio, descripcion, cantidad, imagen FROM productos WHERE id_cat = 2")
        productos_maquinas = cursor.fetchall()
        cursor.close()

        # Pasa la lista de productos de máquinas a la plantilla
        return render_template('secadores_admin.html', lista_productos=productos_maquinas)

    except Error as e:
        print(f"Error al obtener productos de máquinas: {str(e)}")
        # Manejo del error, redirigir o mostrar un mensaje de error según sea necesario
        return render_template('secadores_admin.html', error_message='Error al obtener productos de máquinas')

@app.route('/admin/productos-otros')
def productos_otros_admin():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id, nombre, precio, descripcion, cantidad, imagen FROM productos WHERE id_cat = 3")
        productos_maquinas = cursor.fetchall()
        cursor.close()

        # Pasa la lista de productos de máquinas a la plantilla
        return render_template('otros_admin.html', lista_productos=productos_maquinas)

    except Error as e:
        print(f"Error al obtener productos de máquinas: {str(e)}")
        # Manejo del error, redirigir o mostrar un mensaje de error según sea necesario
        return render_template('otros_admin.html', error_message='Error al obtener productos de máquinas')




# Agregar Producto
@app.route('/admin/agregar-producto', methods=['GET', 'POST'])
def agregar_producto():
    if request.method == 'POST':
        try:
            # Lógica para procesar el formulario de agregar producto y agregar a la base de datos
            nuevo_nombre = request.form.get('nuevo_nombre')
            nuevo_precio = request.form.get('nuevo_precio')

            # Accede al archivo de la solicitud
            nueva_imagen = request.files['nueva_imagen']

            # Obtiene la descripción y cantidad del formulario
            nueva_descripcion = request.form.get('nueva_descripcion')
            nueva_cantidad = request.form.get('nueva_cantidad')

            # Obtiene la categoría del formulario
            id_cat = request.form.get('id_cat')

            # Verifica si se seleccionó una imagen
            if nueva_imagen and allowed_file(nueva_imagen.filename):
                # Guarda la imagen en la carpeta 'static/images'
                filename = secure_filename(nueva_imagen.filename)
                nueva_imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                # Guarda la información del producto en la base de datos
                cursor = db.cursor()
                cursor.execute("INSERT INTO productos (nombre, precio, imagen, descripcion, cantidad, id_cat) VALUES (%s, %s, %s, %s, %s, %s)",
                            (nuevo_nombre, nuevo_precio, filename, nueva_descripcion, nueva_cantidad, id_cat))
                db.commit()
                cursor.close()

                # Redirige a la página inicio después de agregar
                return redirect(url_for('admin'))

        except Error as e:
            print(f"Error al agregar producto: {str(e)}")
            # Manejo del error, redirigir o mostrar un mensaje de error según sea necesario
            return render_template('agregar_producto.html', error_message='Error al agregar producto')

    elif request.method == 'GET':
        # Renderiza el formulario de agregar producto
        return render_template('agregar_producto.html')  # Crea este archivo HTML


# Agrega una función para verificar la extensión del archivo permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}



#---------------------------------------MAQUINAS------------------------------------


@app.route('/admin/productos-maquinas/editar/<int:producto_id>', methods=['GET', 'POST'])
def editar_maquina(producto_id):
    if request.method == 'GET':
        # Lógica para cargar la información del producto y mostrar el formulario de edición
        cursor = db.cursor()
        cursor.execute("SELECT id, nombre, precio, descripcion, cantidad FROM productos WHERE id = %s", (producto_id,))
        producto = cursor.fetchone()
        cursor.close()

        return render_template('editar_producto.html', producto=producto)

    elif request.method == 'POST':
        # Lógica para procesar el formulario de edición y actualizar el producto en la base de datos
        nuevo_nombre = request.form.get('nuevo_nombre')
        nuevo_precio = request.form.get('nuevo_precio')
        nueva_descripcion = request.form.get('nueva_descripcion')
        nueva_cantidad = request.form.get('nueva_cantidad')

        cursor = db.cursor()
        cursor.execute("UPDATE productos SET nombre=%s, precio=%s, descripcion=%s, cantidad=%s WHERE id=%s",
                    (nuevo_nombre, nuevo_precio, nueva_descripcion, nueva_cantidad, producto_id))
        db.commit()
        cursor.close()

        # Redirigir a la página de lista de productos después de editar
        return redirect(url_for('productos_maquinas_admin'))


#---------------------------------------SECADORES-----------------------------------

@app.route('/admin/productos-secadores/editar/<int:producto_id>', methods=['GET', 'POST'])
def editar_secador(producto_id):
    if request.method == 'GET':
        # Lógica para cargar la información del producto y mostrar el formulario de edición
        cursor = db.cursor()
        cursor.execute("SELECT id, nombre, precio, descripcion, cantidad FROM productos WHERE id = %s", (producto_id,))
        producto = cursor.fetchone()
        cursor.close()

        return render_template('editar_producto.html', producto=producto)

    elif request.method == 'POST':
        # Lógica para procesar el formulario de edición y actualizar el producto en la base de datos
        nuevo_nombre = request.form.get('nuevo_nombre')
        nuevo_precio = request.form.get('nuevo_precio')
        nueva_descripcion = request.form.get('nueva_descripcion')
        nueva_cantidad = request.form.get('nueva_cantidad')

        cursor = db.cursor()
        cursor.execute("UPDATE productos SET nombre=%s, precio=%s, descripcion=%s, cantidad=%s WHERE id=%s",
                    (nuevo_nombre, nuevo_precio, nueva_descripcion, nueva_cantidad, producto_id))
        db.commit()
        cursor.close()

        # Redirigir a la página de lista de productos después de editar
        return redirect(url_for('productos_secadores_admin'))

#-------------------------------OTROS ARTICULOS--------------------------------------
    
@app.route('/admin/productos-otros/editar/<int:producto_id>', methods=['GET', 'POST'])
def editar_otro(producto_id):
    if request.method == 'GET':
        # Lógica para cargar la información del producto y mostrar el formulario de edición
        cursor = db.cursor()
        cursor.execute("SELECT id, nombre, precio, descripcion, cantidad FROM productos WHERE id = %s", (producto_id,))
        producto = cursor.fetchone()
        cursor.close()

        return render_template('editar_producto.html', producto=producto)

    elif request.method == 'POST':
        # Lógica para procesar el formulario de edición y actualizar el producto en la base de datos
        nuevo_nombre = request.form.get('nuevo_nombre')
        nuevo_precio = request.form.get('nuevo_precio')
        nueva_descripcion = request.form.get('nueva_descripcion')
        nueva_cantidad = request.form.get('nueva_cantidad')

        cursor = db.cursor()
        cursor.execute("UPDATE productos SET nombre=%s, precio=%s, descripcion=%s, cantidad=%s WHERE id=%s",
                    (nuevo_nombre, nuevo_precio, nueva_descripcion, nueva_cantidad, producto_id))
        db.commit()
        cursor.close()

        # Redirigir a la página de lista de productos después de editar
        return redirect(url_for('productos_otros_admin'))


@app.route('/admin/productos-maquinas/eliminar/<int:producto_id>', methods=['POST'])
def eliminar_producto(producto_id):
    try:
        if request.method == 'POST':
            # Lógica para procesar la solicitud de eliminación y eliminar el producto de la base de datos
            cursor = db.cursor()
            cursor.execute("DELETE FROM productos WHERE id = %s", (producto_id,))
            db.commit()
            cursor.close()

            # Puedes devolver un mensaje JSON indicando el éxito de la operación
            return jsonify({'message': 'Producto eliminado exitosamente'})

    except Error as e:
        print(f"Error inesperado al eliminar producto: {str(e)}")
        # Devuelve un mensaje JSON indicando el error en caso de problemas
        return jsonify({'error': 'Error al eliminar producto'})
    

@app.route('/admin/usuarios/eliminar/<int:usuario_id>', methods=['POST'])
def eliminar_usuario(usuario_id):
    try:
        if request.method == 'POST':
            # Lógica para procesar la solicitud de eliminación y eliminar el usuario de la base de datos
            cursor = db.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (usuario_id,))
            db.commit()
            cursor.close()

            # Puedes devolver un mensaje JSON indicando el éxito de la operación
            return jsonify({'message': 'Usuario eliminado exitosamente'})

    except Error as e:
        print(f"Error inesperado al eliminar usuario: {str(e)}")
        # Devuelve un mensaje JSON indicando el error en caso de problemas
        return jsonify({'error': 'Error al eliminar usuario'})


#------------------------------------FIN ADMIN--------------------------------------------








# ------------------------------ CARRITO DE COMPRAS -----------------------------------------

# Ruta para agregar un producto al carrito
@app.route('/agregar-al-carrito', methods=['POST'])
def agregar_al_carrito():
    if request.method == 'POST':
        try:
            id_producto = request.form.get('id_producto')
            cantidad = request.form.get('cantidad')

            # Crear una instancia del usuario actual (si está autenticado)
            user = User(nombre='', telefono='', correo='', contraseña='', id=session.get('id'))

            # Llamar al método para agregar producto al carrito
            result = user.agregar_producto_al_carrito(id_producto, cantidad)

            return jsonify(result)

        except Exception as e:
            return jsonify({'error': str(e)})

# Ruta para ver el carrito
@app.route('/ver-carrito')
def ver_carrito():
    # Crear una instancia del usuario actual (si está autenticado)
    user = User(nombre='', telefono='', correo='', contraseña='', id=session.get('id'))

    # Llamar al método para obtener el contenido del carrito
    carrito = user.obtener_carrito()

    return render_template('carrito.html', carrito=carrito)

# Ruta para eliminar un producto del carrito
@app.route('/eliminar-del-carrito/<int:id_carrito>', methods=['POST'])
def eliminar_del_carrito(id_carrito):
    # Crear una instancia del usuario actual (si está autenticado)
    user = User(nombre='', telefono='', correo='', contraseña='', id=session.get('id'))

    # Llamar al método para eliminar producto del carrito
    result = user.eliminar_producto_carrito(id_carrito)

    return jsonify(result)


# ------------------------------ Fin CARRITO DE COMPRAS -----------------------------------------





#-------------------------------------Run Aplication-------------------------------------
if __name__=='__main__':
    app.run(debug=True)