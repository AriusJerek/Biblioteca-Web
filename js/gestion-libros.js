const form = document.getElementById("formAgregarLibro");
const lista = document.getElementById("listaLibros");

let libros = JSON.parse(localStorage.getItem("libros")) || [];

let editando = false;
let indexEditando = null;

// Guardar en localStorage
function guardarEnLocalStorage() {
  localStorage.setItem("libros", JSON.stringify(libros));
}

// Mostrar los libros en la lista
function renderLibros(filtro = "") {
  lista.innerHTML = "";

  const librosFiltrados = libros.filter(libro =>
    libro.nombre.toLowerCase().includes(filtro.toLowerCase()) ||
    libro.autor.toLowerCase().includes(filtro.toLowerCase()) ||
    libro.categoria.toLowerCase().includes(filtro.toLowerCase())
  );

  if (librosFiltrados.length === 0) {
    lista.innerHTML = "<li>No hay libros registrados.</li>";
    return;
  }

  librosFiltrados.forEach((libro, index) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <strong>${libro.nombre}</strong><br>
      Autor: ${libro.autor}<br>
      Categoría: ${libro.categoria}<br>
      ${libro.anio ? `Año: ${libro.anio}<br>` : ""}
      ${libro.sinopsis ? `Sinopsis: ${libro.sinopsis}<br>` : ""}
      ${libro.notas ? `Notas: ${libro.notas}<br>` : ""}
      <div class="img">
        ${libro.imagen ? `<img src="${libro.imagen}" alt="Portada del libro" style="max-width:100px;">` : ""}
      </div>
      <div class="acciones">
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
    const nuevoLibro = { nombre, autor, categoria, sinopsis, anio, imagen, notas };

    if (editando) {
      libros[indexEditando] = nuevoLibro;
      editando = false;
      indexEditando = null;
      form.querySelector("button").textContent = "Agregar Libro";
    } else {
      libros.push(nuevoLibro);
    }

    guardarEnLocalStorage();
    renderLibros();
    form.reset();
  }
});

// Editar libro
function editarLibro(index) {
  const libro = libros[index];
  document.getElementById("nombre").value = libro.nombre;
  document.getElementById("autor").value = libro.autor;
  document.getElementById("categoria").value = libro.categoria;
  document.getElementById("sinopsis").value = libro.sinopsis || "";
  document.getElementById("anio").value = libro.anio || "";
  document.getElementById("imagen").value = libro.imagen || "";
  document.getElementById("notas").value = libro.notas || "";

  editando = true;
  indexEditando = index;
  form.querySelector("button").textContent = "Guardar Cambios";
}

// Eliminar libro
function eliminarLibro(index) {
  if (confirm("¿Seguro que deseas eliminar este libro?")) {
    libros.splice(index, 1);
    guardarEnLocalStorage();
    renderLibros();
  }
}

// Buscar libros
const buscador = document.getElementById("buscador");
if (buscador) {
  buscador.addEventListener("input", () => {
    renderLibros(buscador.value);
  });
}

// Inicial
renderLibros();

