const lista = document.getElementById("listaNovedades");
const anuncios = JSON.parse(localStorage.getItem("anuncios")) || [];

anuncios.forEach(anuncio => {
  const li = document.createElement("li");
  li.innerHTML = `<strong>${anuncio.fecha}:</strong> ${anuncio.mensaje}`;
  lista.appendChild(li);
});
