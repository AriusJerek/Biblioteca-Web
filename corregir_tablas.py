import sqlite3

DB = 'database/basedatos.db'
SECCIONES = ['000','100','200','300','400','500','600','700','800','900']

conn = sqlite3.connect(DB)
c = conn.cursor()

for seccion in SECCIONES:
    tabla = f'libros_{seccion}'
    # Verificar si la tabla existe antes de operar
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabla,))
    if not c.fetchone():
        print(f"Tabla {tabla} no existe, se omite.")
        continue
    # Obtener columnas actuales
    c.execute(f"PRAGMA table_info({tabla})")
    columnas = [col[1] for col in c.fetchall()]
    if 'id' not in columnas:
        # Crear tabla temporal con id autoincrement
        c.execute(f'''CREATE TABLE IF NOT EXISTS temp_{tabla} (
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
        # Solo copiar columnas que existan en la tabla original y en la nueva
        cols_to_copy = ','.join([col for col in ['cantidad','codigo','categoria','nombre','autor','estado','origen','imagen'] if col in columnas])
        if cols_to_copy:
            c.execute(f'INSERT INTO temp_{tabla} ({cols_to_copy}) SELECT {cols_to_copy} FROM {tabla}')
        # Eliminar tabla original y renombrar la temporal
        c.execute(f'DROP TABLE {tabla}')
        c.execute(f'ALTER TABLE temp_{tabla} RENAME TO {tabla}')
        print(f"Tabla {tabla} corregida con columna id.")
    else:
        print(f"Tabla {tabla} ya tiene columna id.")

conn.commit()
conn.close()
print("Estructura de tablas corregida.")
