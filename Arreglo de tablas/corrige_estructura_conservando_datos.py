import sqlite3

secciones = ['000','100','200','300','400','500','600','700','800','900']

estructura = [
    ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
    ('cantidad', 'INTEGER'),
    ('codigo', 'TEXT'),
    ('categoria', 'TEXT'),
    ('nombre', 'TEXT'),
    ('autor', 'TEXT'),
    ('estado', 'TEXT'),
    ('origen', 'TEXT'),
    ('imagen', 'TEXT')
]

conn = sqlite3.connect('database/basedatos.db')
c = conn.cursor()

for seccion in secciones:
    tabla = f'libros_{seccion}'
    c.execute(f"PRAGMA table_info({tabla})")
    cols_actuales = [col[1] for col in c.fetchall()]
    if 'id' not in cols_actuales:
        print(f"Corrigiendo {tabla}...")
        # Renombrar tabla original
        c.execute(f"ALTER TABLE {tabla} RENAME TO {tabla}_old")
        # Crear nueva tabla con id autoincremental
        cols_sql = ', '.join([f'{col} {tipo}' for col, tipo in estructura])
        c.execute(f"CREATE TABLE {tabla} ({cols_sql})")
        # Copiar datos (sin id)
        cols_sin_id = [col for col, tipo in estructura if col != 'id']
        cols_str = ', '.join(cols_sin_id)
        c.execute(f"INSERT INTO {tabla} ({cols_str}) SELECT {cols_str} FROM {tabla}_old")
        c.execute(f"DROP TABLE {tabla}_old")
        print(f"Tabla {tabla} migrada correctamente.")
    else:
        print(f"Tabla {tabla} ya tiene id autoincremental.")

conn.commit()
conn.close()
print("¡Estructura de todas las tablas corregida y datos conservados!")
