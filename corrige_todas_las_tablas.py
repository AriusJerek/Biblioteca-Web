# corrige_todas_las_tablas.py
import sqlite3

secciones = ['000','100','200','300','400','500','600','700','800','900']

conn = sqlite3.connect('database/basedatos.db')
c = conn.cursor()

for seccion in secciones:
    tabla = f'libros_{seccion}'
    print(f"Eliminando y recreando tabla {tabla}...")
    # Eliminar la tabla si existe
    c.execute(f'DROP TABLE IF EXISTS {tabla}')
    # Crear la nueva tabla con la estructura correcta
    c.execute(f'''
        CREATE TABLE {tabla} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cantidad INTEGER,
            codigo TEXT,
            categoria TEXT,
            nombre TEXT,
            autor TEXT,
            estado TEXT,
            origen TEXT,
            imagen TEXT
        )
    ''')
    print(f"Tabla {tabla} creada.")

conn.commit()
conn.close()
print("¡Todas las tablas han sido eliminadas y recreadas!")
