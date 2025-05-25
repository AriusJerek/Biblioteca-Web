import sqlite3

DB = 'database/basedatos.db'
SECCIONES = ['000','100','200','300','400','500','600','700','800','900']

conn = sqlite3.connect(DB)
c = conn.cursor()

for seccion in SECCIONES:
    tabla = f'libros_{seccion}'
    c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabla,))
    if not c.fetchone():
        c.execute(f'''CREATE TABLE {tabla} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cantidad INTEGER,
            codigo TEXT,
            categoria TEXT,
            nombre TEXT,
            autor TEXT,
            estado TEXT,
            origen TEXT,
            imagen TEXT
        )''')
        print(f"Tabla {tabla} creada correctamente.")
    else:
        print(f"Tabla {tabla} ya existe.")

conn.commit()
conn.close()
print("Tablas de libros por sección creadas si no existían.")
