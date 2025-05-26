# excel_a_sql.py
import pandas as pd
import sqlite3

# Mapas de nombres alternativos a los nombres estándar
col_map = {
    'cantidad': ['cantidad', 'Cantidad', 'CANTIDAD'],
    'codigo': ['codigo', 'código', 'Codigo', 'Código', 'CODIGO', 'CÓDIGO'],
    'categoria': ['categoria', 'categoría', 'Categoria', 'Categoría', 'CATEGORIA', 'CATEGORÍA'],
    'nombre': ['nombre', 'Nombre', 'NOMBRE'],
    'autor': ['autor', 'Autor', 'AUTOR'],
    'estado': ['estado', 'Estado', 'ESTADO'],
    'origen': ['origen', 'Origen', 'ORIGEN'],
    'imagen': ['imagen', 'Imagen', 'IMAGEN', 'portada', 'Portada', 'PORTADA']
}
def normaliza_columnas(df):
    nuevo = {}
    for estandar, variantes in col_map.items():
        for v in variantes:
            if v in df.columns:
                nuevo[estandar] = df[v]
                break
        else:
            nuevo[estandar] = ''  # Si no existe, poner vacío
    return pd.DataFrame(nuevo)

# Cargar Excel con varias hojas
archivo = pd.ExcelFile('libros.xlsx')

# Conectarse (o crear) la base de datos
conn = sqlite3.connect('database/basedatos.db')

# Listado de hojas que quieres importar como tablas independientes
hojas_tablas = ['000','100','200','300','400','500','600','700','800','900']

for hoja in hojas_tablas:
    if hoja in archivo.sheet_names:
        df = archivo.parse(hoja)
        df = normaliza_columnas(df)
        df.to_sql(f'libros_{hoja}', conn, if_exists='replace', index=False)

# Si tienes una hoja de alumnos, también la puedes cargar igual:
if 'Alumnos' in archivo.sheet_names:
    df_alumnos = archivo.parse('Alumnos')
    df_alumnos.to_sql('alumnos', conn, if_exists='replace', index=False)

conn.close()
print("Base de datos actualizada con éxito.")
