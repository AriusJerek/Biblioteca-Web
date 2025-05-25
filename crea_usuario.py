# crea_usuario.py
import sqlite3
import bcrypt

conn = sqlite3.connect('database/usuarios.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')

def crear_usuario(username, password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    c.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (username, hashed.decode('utf-8')))

usuario = input('Usuario: ')
clave = input('Contraseña: ')
crear_usuario(usuario, clave)

conn.commit()
conn.close()
print("Usuario creado.")
