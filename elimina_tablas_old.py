# elimina_tablas_old.py
import sqlite3

conn = sqlite3.connect('database/basedatos.db')
c = conn.cursor()

# Buscar todas las tablas que terminan en _old (sin escapes problemáticos)
tablas_old = [row[0] for row in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_old'")]

for tabla in tablas_old:
    print(f"Eliminando tabla temporal: {tabla}")
    c.execute(f'DROP TABLE IF EXISTS {tabla}')

conn.commit()
conn.close()
print("¡Tablas temporales _old eliminadas!")
