const lista = document.getElementById("lista-novedades");
const anuncios = JSON.parse(localStorage.getItem("anuncios")) || [];

anuncios.forEach(anuncio => {
  const li = document.createElement("li");
  li.innerHTML = `<strong>${anuncio.fecha}:</strong> ${anuncio.mensaje}`;
  lista.appendChild(li);
});
