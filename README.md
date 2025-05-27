# Biblioteca Web

Sistema de gestión y visualización del material de la biblioteca.

## Descripción
Este proyecto es una aplicación web para la administración y consulta de libros, anuncios y alumnos de una biblioteca. Permite a los usuarios autenticados gestionar el catálogo de libros, publicar anuncios y visualizar información relevante. Los visitantes pueden explorar el catálogo y ver anuncios públicos.

## Características principales
- Visualización de catálogo de libros por secciones, con vista previa atractiva.
- Búsqueda de libros por nombre, autor o categoría.
- Visualización de anuncios y novedades públicas.
- Página pública para alumnos y visitantes con catálogo y anuncios.
- Gestión de libros (agregar, editar, eliminar) para administradores.
- Gestión de anuncios y novedades (solo administradores).
- Listado de alumnos registrados (solo administradores).
- Autenticación de usuarios para acceso administrativo.

## Tecnologías utilizadas
- Python 3
- Flask
- SQLite3
- HTML, CSS, JavaScript
- bcrypt (para contraseñas seguras)

## Instalación y requisitos
1. **Clona el repositorio o descarga los archivos.**
2. **(Opción 1: Instalación tradicional)**
   - Instala las dependencias necesarias:
     ```bash
     pip install flask bcrypt pandas
     ```
   - Asegúrate de tener Python 3 instalado.
   - Crea las bases de datos y tablas ejecutando los scripts:
     ```bash
     python crear_tablas_libros.py
     python crea_usuario.py
     python excel_a_sql.py
     ```
     (Sigue las instrucciones para crear un usuario administrador y cargar los datos de libros/alumnos desde el Excel.)
   - Inicia la aplicación:
     ```bash
     python app.py
     ```
   - Accede a `http://localhost:5000` desde tu navegador.

3. **(Opción 2: Usar Docker - Recomendado para portabilidad)**
   - Asegúrate de tener [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado en tu máquina.
   - Abre una terminal en la carpeta del proyecto (donde está el `Dockerfile`).
   - Construye la imagen Docker:
     ```powershell
     docker build -t biblioteca-web .
     ```
   - Ejecuta el contenedor, montando la carpeta `database/` para persistencia de datos:
     ```powershell
     docker run -p 5000:5000 -v ${PWD}\database:/app/database biblioteca-web
     ```
     > Si usas Linux/Mac, reemplaza la barra invertida por barra normal: `${PWD}/database:/app/database`
   - Accede a `http://localhost:5000` desde tu navegador.
   - Si necesitas crear las tablas o cargar datos, ejecuta los scripts auxiliares dentro del contenedor o en tu máquina antes de iniciar la app.

4. **Variables de entorno (opcional)**
   - Puedes definir la clave secreta de Flask al ejecutar el contenedor:
     ```powershell
     docker run -p 5000:5000 -v ${PWD}\database:/app/database -e SECRET_KEY=miclave biblioteca-web
     ```
   - Asegúrate de que tu `app.py` lea la variable de entorno `SECRET_KEY` (ya preparado en el código si seguiste las recomendaciones).

## Estructura del proyecto
- `app.py`: Aplicación principal Flask.
- `database/`: Bases de datos SQLite (`basedatos.db`, `usuarios.db`).
- `static/`: Archivos estáticos (CSS, imágenes, navbar).
- `templates/`: Plantillas HTML.
- `libros.xlsx`, `libros_ejemplo.csv`: Datos de ejemplo para cargar libros.
- Scripts auxiliares:
  - `crear_tablas_libros.py`: Crea tablas de libros por sección.
  - `crea_usuario.py`: Crea usuarios administradores.
  - `excel_a_sql.py`: Importa datos desde Excel a la base de datos.
  - `corregir_tablas.py`: Corrige estructura de tablas si es necesario.

## Público general y alumnos
- El catálogo y los anuncios son accesibles para cualquier visitante.
- La página pública muestra los libros en formato de tarjetas con imagen, nombre, autor y categoría.
- Los alumnos pueden buscar libros y ver novedades sin necesidad de iniciar sesión.

## Administración
- El acceso a la gestión de libros, anuncios y alumnos está protegido por autenticación.
- Solo los usuarios administradores pueden modificar el catálogo y los anuncios.

## Créditos
Desarrollado por el estudiante - Josias Asael Alvarez Jara.

## Licencia
Uso interno educativo. Puedes adaptar el sistema según tus necesidades.
