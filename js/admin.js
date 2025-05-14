document.getElementById("loginForm").addEventListener("submit", function(e) {
  e.preventDefault();

  const usuario = document.getElementById("usuario").value;
  const contrasena = document.getElementById("contrasena").value;
  const error = document.getElementById("error");

  // Credenciales simuladas
  if (usuario === "Maria" && contrasena === "131619") {
    window.location.href = "panel.html";
  } else {
    error.textContent = "Credenciales incorrectas. Intenta nuevamente.";
  }
});
