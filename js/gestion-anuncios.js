const form = document.getElementById("formAnuncio");
const lista = document.getElementById("listaAnuncios");
let anuncios = JSON.parse(localStorage.getItem("anuncios")) || [];

function mostrarAnuncios() {
  lista.innerHTML = "";
  anuncios.forEach((anuncio, index) => {
    const li = document.createElement("li");
    li.classList.add("anuncio-item");
    li.innerHTML = `
      <span class="fecha">${anuncio.fecha}:</span> ${anuncio.mensaje}
      <button class="btn-eliminar" onclick="eliminarAnuncio(${index})">🗑️ Eliminar</button>
    `;
    lista.appendChild(li);
  });
}

function eliminarAnuncio(index) {
  if (confirm("¿Seguro que deseas eliminar este anuncio?")) {
    anuncios.splice(index, 1);
    localStorage.setItem("anuncios", JSON.stringify(anuncios));
    mostrarAnuncios();
  }
}

form.addEventListener("submit", function (e) {
  e.preventDefault();

  const fecha = document.getElementById("fecha").value;
  const mensaje = document.getElementById("mensaje").value.trim();

  if (fecha && mensaje) {
    anuncios.push({ fecha, mensaje });
    localStorage.setItem("anuncios", JSON.stringify(anuncios));
    form.reset();
    mostrarAnuncios();
  }
});

mostrarAnuncios();

