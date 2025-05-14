const contenedor = document.getElementById("catalogo");
const libros = JSON.parse(localStorage.getItem("libros")) || [];

libros.forEach((libro, index) => {
  const div = document.createElement("div");
  div.className = "libro";
  div.innerHTML = `
    <h2>${libro.nombre}</h2>
    <p><strong>Autor:</strong> ${libro.autor}</p>
    <p><strong>Categoría:</strong> ${libro.categoria}</p>
    <a href="libro.html?id=${index}" class="btn">Ver más</a>
  `;
  contenedor.appendChild(div);
});
