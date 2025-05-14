const form = document.getElementById("formAgregarLibro");
const lista = document.getElementById("listaLibros");

// Obtener libros del localStorage o crear un arreglo vacío
let libros = JSON.parse(localStorage.getItem("libros")) || [];

// Guardar en localStorage
function guardarEnLocalStorage() {
  localStorage.setItem("libros", JSON.stringify(libros));
}

// Mostrar los libros en la lista
function renderLibros() {
  lista.innerHTML = "";

  if (libros.length === 0) {
    lista.innerHTML = "<li>No hay libros registrados.</li>";
    return;
  }

  libros.forEach((libro, index) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <strong>${libro.nombre}</strong><br>
      Autor: ${libro.autor}<br>
      Categoría: ${libro.categoria}
      <div class="img">
       ${libro.imagen ? `<img src="${libro.imagen}" alt="Portada del libro" style="max-width:100px;">` : ""}
      </div>
      <div class = "acciones">
      <button onclick="editarLibro(${index})">Editar</button>
      <button onclick="eliminarLibro(${index})">Eliminar</button>
      </div>
    `;
    lista.appendChild(li);
    
  });
}


// Manejar envío del formulario
form.addEventListener("submit", (e) => {
  e.preventDefault();

  const nombre = document.getElementById("nombre").value.trim();
  const autor = document.getElementById("autor").value.trim();
  const categoria = document.getElementById("categoria").value.trim();
  const sinopsis = document.getElementById("sinopsis").value.trim();
  const anio = document.getElementById("anio").value.trim();
  const imagen = document.getElementById("imagen").value.trim();
  const notas = document.getElementById("notas").value.trim();

  if (nombre && autor && categoria) {
    libros.push({ nombre, autor, categoria, sinopsis, anio, imagen, notas });
    guardarEnLocalStorage();
    renderLibros();  // ✅ Actualiza la lista en la misma página
    form.reset();
  
}
});

// Editar libro
function editarLibro(index) {
  const libro = libros[index];
  document.getElementById("nombre").value = libro.nombre;
  document.getElementById("autor").value = libro.autor;
  document.getElementById("categoria").value = libro.categoria;
  editando = true;
  indexEditando = index;
  form.querySelector("button").textContent = "Guardar Cambios";
  

  
  // Eliminar el libro original
  libros.splice(index, 1);
  guardarEnLocalStorage();
  renderLibros();
}

// Eliminar libro
function eliminarLibro(index) {
  libros.splice(index, 1);
  guardarEnLocalStorage();
  renderLibros();
}

// Cargar los libros al iniciar la página
renderLibros();
// Evento de búsqueda
// Búsqueda en tiempo real
buscador.addEventListener("input", () => {
  renderLibros(buscador.value);
});
