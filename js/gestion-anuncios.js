const form = document.getElementById("formAnuncio");
const lista = document.getElementById("listaAnuncios");
let anuncios = JSON.parse(localStorage.getItem("anuncios")) || [];

function mostrarAnuncios() {
  lista.innerHTML = "";
  anuncios.forEach((anuncio, index) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <strong>${anuncio.fecha}:</strong> ${anuncio.mensaje}
      <button onclick="eliminarAnuncio(${index})" style="margin-left: 10px;">🗑️ Eliminar</button>
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


form.addEventListener("submit", function(e) {
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
