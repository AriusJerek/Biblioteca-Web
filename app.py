from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import bcrypt
import re
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '131619'

DATABASE_USUARIOS = 'database/usuarios.db'
DATABASE_LIBROS = 'database/basedatos.db'

UPLOAD_FOLDER = 'static/img/libros'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Validación de usuario para login
def validar_usuario(username, password):
    conn = sqlite3.connect(DATABASE_USUARIOS)
    c = conn.cursor()
    c.execute("SELECT password FROM usuarios WHERE username=?", (username,))
    resultado = c.fetchone()
    conn.close()
    if resultado:
        hashed = resultado[0]
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    return False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Vistas ---
@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/catalogo')
def catalogo():
    return render_template('catalogo.html')


# --- API para libros por sección ---
@app.route('/api/libros/<seccion>', methods=['GET'])
def api_libros_seccion(seccion):
    # Paginación: ?page=1&limit=50
    tabla = f'libros_{seccion}'
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=50, type=int)
    offset = (page - 1) * limit
    conn = sqlite3.connect(DATABASE_LIBROS)
    conn.row_factory = sqlite3.Row
    try:
        total = conn.execute(f'SELECT COUNT(*) FROM {tabla}').fetchone()[0]
        libros = conn.execute(f'SELECT * FROM {tabla} LIMIT ? OFFSET ?', (limit, offset)).fetchall()
    except sqlite3.OperationalError:
        conn.close()
        return jsonify({'error': f'No existe la sección {seccion}'}), 404
    conn.close()
    return jsonify({
        'libros': [dict(libro) for libro in libros],
        'total': total,
        'page': page,
        'limit': limit
    })

@app.route('/api/libros/<seccion>', methods=['POST'])
def agregar_libro_seccion(seccion):
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    if not re.fullmatch(r'\d{3}', seccion):
        return jsonify({'error': 'Sección inválida'}), 400
    # Soporta tanto JSON como multipart/form-data
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        form = request.form
        files = request.files
        cantidad = form.get('cantidad')
        codigo = form.get('codigo')
        categoria = form.get('categoria')
        nombre = form.get('nombre')
        autor = form.get('autor')
        estado = form.get('estado')
        origen = form.get('origen')
        imagen_url = form.get('imagen')
        imagen_file = files.get('imagenArchivo')
        imagen = None
        if imagen_file and allowed_file(imagen_file.filename):
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            filename = secure_filename(imagen_file.filename)
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Evitar sobrescribir archivos
            base, ext = os.path.splitext(filename)
            i = 1
            while os.path.exists(ruta):
                filename = f"{base}_{i}{ext}"
                ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                i += 1
            imagen_file.save(ruta)
            imagen = '/' + ruta.replace('\\', '/').replace('static/', 'static/')
        elif imagen_url:
            imagen = imagen_url
    else:
        data = request.get_json()
        cantidad = data.get('cantidad')
        codigo = data.get('codigo')
        categoria = data.get('categoria')
        nombre = data.get('nombre')
        autor = data.get('autor')
        estado = data.get('estado')
        origen = data.get('origen')
        imagen = data.get('imagen')
    # Validar campos obligatorios
    if not all([nombre, autor, categoria, codigo, estado, origen, cantidad]):
        return jsonify({'error': 'Datos incompletos'}), 400
    try:
        cantidad = int(cantidad)
        if cantidad < 1:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'error': 'Cantidad inválida'}), 400
    tabla = f'libros_{seccion}'
    try:
        with sqlite3.connect(DATABASE_LIBROS) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute(f'INSERT INTO {tabla} (cantidad, codigo, categoria, nombre, autor, estado, origen, imagen) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                      (cantidad, codigo, categoria, nombre, autor, estado, origen, imagen))
            conn.commit()
            libros = c.execute(f'SELECT * FROM {tabla}').fetchall()
            return jsonify({'libros': [dict(libro) for libro in libros]}), 201
    except sqlite3.OperationalError:
        return jsonify({'error': 'Sección no encontrada'}), 404
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Error de integridad en los datos'}), 400
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor', 'detalle': str(e)}), 500

@app.route('/api/libros/<seccion>/<int:libro_id>', methods=['DELETE'])
def eliminar_libro_seccion(seccion, libro_id):
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    if not re.fullmatch(r'\d{3}', seccion):
        return jsonify({'error': 'Sección inválida'}), 400
    tabla = f'libros_{seccion}'
    try:
        with sqlite3.connect(DATABASE_LIBROS) as conn:
            c = conn.cursor()
            # Obtener la ruta de la imagen antes de eliminar
            c.execute(f'SELECT imagen FROM {tabla} WHERE id=?', (libro_id,))
            row = c.fetchone()
            imagen = row[0] if row else None
            # Eliminar el libro
            c.execute(f'DELETE FROM {tabla} WHERE id=?', (libro_id,))
            conn.commit()
            if c.rowcount == 0:
                return jsonify({'error': 'Libro no encontrado'}), 404
            # Eliminar la imagen física si es local
            if imagen and imagen.startswith('/static/img/libros/') and not imagen.startswith('http'):
                ruta_fisica = imagen.lstrip('/')
                if os.path.exists(ruta_fisica):
                    try:
                        os.remove(ruta_fisica)
                    except Exception:
                        pass  # Ignorar errores al borrar archivo
            return jsonify({'success': True})
    except sqlite3.OperationalError:
        return jsonify({'error': 'Sección no encontrada'}), 404
    except Exception:
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/libros/<seccion>/<int:libro_id>', methods=['PUT'])
def editar_libro_seccion(seccion, libro_id):
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    if not re.fullmatch(r'\d{3}', seccion):
        return jsonify({'error': 'Sección inválida'}), 400
    # Soporta tanto JSON como multipart/form-data
    if request.content_type and request.content_type.startswith('multipart/form-data'):
        form = request.form
        files = request.files
        cantidad = form.get('cantidad')
        codigo = form.get('codigo')
        categoria = form.get('categoria')
        nombre = form.get('nombre')
        autor = form.get('autor')
        estado = form.get('estado')
        origen = form.get('origen')
        imagen_url = form.get('imagen')
        imagen_file = files.get('imagenArchivo')
        imagen = None
        imagen_anterior = None
        # Obtener la imagen anterior si se va a reemplazar o eliminar
        with sqlite3.connect(DATABASE_LIBROS) as conn:
            c = conn.cursor()
            c.execute(f'SELECT imagen FROM libros_{seccion} WHERE id=?', (libro_id,))
            row = c.fetchone()
            imagen_anterior = row[0] if row else None
        if imagen_file and allowed_file(imagen_file.filename):
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            filename = secure_filename(imagen_file.filename)
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            base, ext = os.path.splitext(filename)
            i = 1
            while os.path.exists(ruta):
                filename = f"{base}_{i}{ext}"
                ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                i += 1
            imagen_file.save(ruta)
            imagen = '/' + ruta.replace('\\', '/').replace('static/', 'static/')
            # Eliminar la imagen anterior si era local y distinta
            if imagen_anterior and imagen_anterior.startswith('/static/img/libros/') and not imagen_anterior.startswith('http') and imagen_anterior != imagen:
                ruta_fisica = imagen_anterior.lstrip('/')
                if os.path.exists(ruta_fisica):
                    try:
                        os.remove(ruta_fisica)
                    except Exception:
                        pass
        elif imagen_url == '':  # Si se envía imagen vacía, eliminar la imagen anterior
            if imagen_anterior and imagen_anterior.startswith('/static/img/libros/') and not imagen_anterior.startswith('http'):
                ruta_fisica = imagen_anterior.lstrip('/')
                if os.path.exists(ruta_fisica):
                    try:
                        os.remove(ruta_fisica)
                    except Exception:
                        pass
            imagen = ''
        elif imagen_url:
            imagen = imagen_url
        else:
            imagen = imagen_anterior
    else:
        data = request.get_json()
        cantidad = data.get('cantidad')
        codigo = data.get('codigo')
        categoria = data.get('categoria')
        nombre = data.get('nombre')
        autor = data.get('autor')
        estado = data.get('estado')
        origen = data.get('origen')
        imagen = data.get('imagen')
    if not all([nombre, autor, categoria, codigo, estado, origen, cantidad]):
        return jsonify({'error': 'Datos incompletos'}), 400
    try:
        cantidad = int(cantidad)
        if cantidad < 1:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({'error': 'Cantidad inválida'}), 400
    tabla = f'libros_{seccion}'
    try:
        with sqlite3.connect(DATABASE_LIBROS) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute(
                f'UPDATE {tabla} SET cantidad=?, codigo=?, categoria=?, nombre=?, autor=?, estado=?, origen=?, imagen=? WHERE id=?',
                (cantidad, codigo, categoria, nombre, autor, estado, origen, imagen, libro_id)
            )
            conn.commit()
            if c.rowcount == 0:
                return jsonify({'error': 'Libro no encontrado'}), 404
            libros = c.execute(f'SELECT * FROM {tabla}').fetchall()
            return jsonify({'libros': [dict(libro) for libro in libros]})
    except sqlite3.OperationalError:
        return jsonify({'error': 'Sección no encontrada'}), 404
    except Exception:
        return jsonify({'error': 'Error interno del servidor'}), 500

# --- API para alumnos ---
@app.route('/api/alumnos')
def api_alumnos():
    conn = sqlite3.connect(DATABASE_LIBROS)
    conn.row_factory = sqlite3.Row
    alumnos = conn.execute('SELECT * FROM alumnos').fetchall()
    conn.close()
    return jsonify([dict(alumno) for alumno in alumnos])

# --- API para agregar alumno ---
@app.route('/api/alumnos', methods=['POST'])
def agregar_alumno():
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    data = request.get_json()
    nombre = data.get('nombre')
    codigo = data.get('codigo')
    if not nombre or not codigo:
        return jsonify({'error': 'Datos incompletos'}), 400
    try:
        with sqlite3.connect(DATABASE_LIBROS) as conn:
            c = conn.cursor()
            c.execute('INSERT INTO alumnos (nombre, codigo) VALUES (?, ?)', (nombre, codigo))
            conn.commit()
        return jsonify({'success': True}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Código de alumno duplicado'}), 400
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor', 'detalle': str(e)}), 500

# --- API para anuncios ---
@app.route('/api/anuncios', methods=['GET'])
def api_anuncios():
    conn = sqlite3.connect(DATABASE_LIBROS)
    conn.row_factory = sqlite3.Row
    anuncios = conn.execute('SELECT * FROM anuncios ORDER BY fecha DESC').fetchall()
    conn.close()
    return jsonify([dict(anuncio) for anuncio in anuncios])

@app.route('/api/anuncios', methods=['POST'])
def agregar_anuncio():
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    data = request.get_json()
    fecha = data.get('fecha')
    mensaje = data.get('mensaje')
    if not fecha or not mensaje:
        return jsonify({'error': 'Datos incompletos'}), 400
    conn = sqlite3.connect(DATABASE_LIBROS)
    c = conn.cursor()
    c.execute('INSERT INTO anuncios (fecha, mensaje) VALUES (?, ?)', (fecha, mensaje))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/anuncios/<int:anuncio_id>', methods=['DELETE'])
def eliminar_anuncio(anuncio_id):
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    conn = sqlite3.connect(DATABASE_LIBROS)
    c = conn.cursor()
    c.execute('DELETE FROM anuncios WHERE id=?', (anuncio_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# --- Eliminar alumno ---
@app.route('/api/alumnos/<int:alumno_id>', methods=['DELETE'])
def eliminar_alumno(alumno_id):
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    try:
        with sqlite3.connect(DATABASE_LIBROS) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM alumnos WHERE id=?', (alumno_id,))
            if c.rowcount == 0:
                return jsonify({'error': 'Alumno no encontrado'}), 404
            conn.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor', 'detalle': str(e)}), 500

# --- Decorador para rutas protegidas ---
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Aplicar decorador a rutas protegidas
@app.route('/panel')
@login_required
def panel():
    return render_template('panel.html')

@app.route('/gestion')
@login_required
def gestion():
    return render_template('gestion-libros.html')

@app.route('/alumnos')
@login_required
def alumnos():
    return render_template('alumnos.html')

@app.route('/anuncios')
@login_required
def anuncios():
    return render_template('gestion-anuncios.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        if validar_usuario(usuario, contrasena):
            session['usuario'] = usuario
            return redirect(url_for('panel'))
        else:
            error = 'Claves incorrectas'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
