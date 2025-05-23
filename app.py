from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import bcrypt
import re

app = Flask(__name__)
app.secret_key = '131619'

DATABASE_USUARIOS = 'database/usuarios.db'
DATABASE_LIBROS = 'database/basedatos.db'

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

# Inicialización de la base de datos de anuncios
def init_db():
    conn = sqlite3.connect(DATABASE_USUARIOS)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS anuncios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        mensaje TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

# --- Vistas ---
@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/catalogo')
def catalogo():
    return render_template('catalogo.html')

@app.route('/alumnos')
def alumnos():
    return render_template('alumnos.html')

@app.route('/panel')
def panel():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('panel.html')

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

@app.route('/gestion')
def gestion():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('gestion-libros.html')

@app.route('/anuncios')
def anuncios():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('gestion-anuncios.html')


# --- API para libros ---
@app.route('/api/libros', methods=['GET'])
def api_libros():
    # Por compatibilidad, mostrar libros de la sección 000 por defecto
    conn = sqlite3.connect(DATABASE_LIBROS)
    conn.row_factory = sqlite3.Row
    try:
        libros = conn.execute('SELECT * FROM libros_000').fetchall()
    except sqlite3.OperationalError:
        conn.close()
        return jsonify([])
    conn.close()
    return jsonify([dict(libro) for libro in libros])

@app.route('/api/libros', methods=['POST'])
def agregar_libro():
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    data = request.get_json()
    cantidad = data.get('cantidad')
    codigo = data.get('codigo')
    categoria = data.get('categoria')
    nombre = data.get('nombre')
    autor = data.get('autor')
    estado = data.get('estado')
    origen = data.get('origen')
    imagen = data.get('imagen')
    if not nombre or not autor or not categoria or not codigo or not estado or not origen or not cantidad:
        return jsonify({'error': 'Datos incompletos'}), 400
    conn = sqlite3.connect(DATABASE_LIBROS)
    c = conn.cursor()
    c.execute('INSERT INTO libros (cantidad, codigo, categoria, nombre, autor, estado, origen, imagen) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
              (cantidad, codigo, categoria, nombre, autor, estado, origen, imagen))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/libros/<int:libro_id>', methods=['DELETE'])
def eliminar_libro(libro_id):
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    conn = sqlite3.connect(DATABASE_LIBROS)
    c = conn.cursor()
    c.execute('DELETE FROM libros WHERE id=?', (libro_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# Endpoint dinámico para consultar libros de una sección específica
@app.route('/api/libros/<seccion>', methods=['GET'])
def api_libros_seccion(seccion):
    tabla = f'libros_{seccion}'
    conn = sqlite3.connect(DATABASE_LIBROS)
    conn.row_factory = sqlite3.Row
    try:
        libros = conn.execute(f'SELECT * FROM {tabla}').fetchall()
    except sqlite3.OperationalError:
        conn.close()
        return jsonify({'error': f'No existe la sección {seccion}'}), 404
    conn.close()
    return jsonify([dict(libro) for libro in libros])

@app.route('/api/libros/<seccion>', methods=['POST'])
def agregar_libro_seccion(seccion):
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    # Validar que la sección solo contenga dígitos (ej: '000', '100', etc.)
    if not re.fullmatch(r'\d{3}', seccion):
        return jsonify({'error': 'Sección inválida'}), 400
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
    # Validar que cantidad sea un entero positivo
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
            return jsonify([dict(libro) for libro in libros]), 201
    except sqlite3.OperationalError:
        return jsonify({'error': 'Sección no encontrada'}), 404
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Error de integridad en los datos'}), 400
    except Exception:
        return jsonify({'error': 'Error interno del servidor'}), 500

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
            c.execute(f'DELETE FROM {tabla} WHERE id=?', (libro_id,))
            conn.commit()
            if c.rowcount == 0:
                return jsonify({'error': 'Libro no encontrado'}), 404
            return jsonify({'success': True})
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

# --- API para anuncios ---
@app.route('/api/anuncios', methods=['GET'])
def api_anuncios():
    conn = sqlite3.connect(DATABASE_USUARIOS)
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
    conn = sqlite3.connect(DATABASE_USUARIOS)
    c = conn.cursor()
    c.execute('INSERT INTO anuncios (fecha, mensaje) VALUES (?, ?)', (fecha, mensaje))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/anuncios/<int:anuncio_id>', methods=['DELETE'])
def eliminar_anuncio(anuncio_id):
    if 'usuario' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    conn = sqlite3.connect(DATABASE_USUARIOS)
    c = conn.cursor()
    c.execute('DELETE FROM anuncios WHERE id=?', (anuncio_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

init_db()

if __name__ == '__main__':
    app.run(debug=True)
