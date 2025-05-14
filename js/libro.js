// Función para obtener parámetros de la URL
function getParametroURL(nombre) {
  const params = new URLSearchParams(window.location.search);
  return params.get(nombre);
}

// Obtener el ID del libro desde la URL
const id = getParametroURL("id");
const contenedor = document.getElementById("detalleLibro");

const libros = JSON.parse(localStorage.getItem("libros")) || [];

if (id !== null && libros[id]) {
  const libro = libros[id];
  contenedor.innerHTML = `
    <h2>${libro.nombre}</h2>
    <p><strong>Autor:</strong> ${libro.autor}</p>
    <p><strong>Categoría:</strong> ${libro.categoria}</p>
    ${libro.anio ? `<p><strong>Año:</strong> ${libro.anio}</p>` : ""}
    ${libro.sinopsis ? `<p><strong>Sinopsis:</strong> ${libro.sinopsis}</p>` : ""}
    ${libro.notas ? `<p><strong>Notas:</strong> ${libro.notas}</p>` : ""}
    ${libro.imagen ? `<img src="${libro.imagen}" alt="Portada del libro" style="max-width:200px;">` : ""}
  `;
} else {
  contenedor.innerHTML = "<p>📕 Libro no encontrado.</p>";
}
