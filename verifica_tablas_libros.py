import sqlite3

secciones = ['000','100','200','300','400','500','600','700','800','900']

conn = sqlite3.connect('database/basedatos.db')
c = conn.cursor()
print('--- Estructura de tablas ---')
errores = False
for s in secciones:
    try:
        c.execute(f'PRAGMA table_info(libros_{s})')
        cols = [col[1] for col in c.fetchall()]
        print(f'libros_{s}:', cols)
        if 'id' not in cols:
            print(f'FALTA id en libros_{s}')
            errores = True
    except Exception as e:
        print(f'Error en libros_{s}:', e)
        errores = True
conn.close()
print('--- Fin ---')
if errores:
    exit(1)
else:
    exit(0)
