function togglePasswordVisibility() {
  var contraseñaInput = document.getElementById("contraseña");
  var iconoOjo = document.querySelector(".fi-sr-eye");

  if (contraseñaInput.type == "password") {
    contraseñaInput.type = "text";
    iconoOjo.classList.remove("fi-sr-eye");
    iconoOjo.classList.add("fi-sr-eye-crossed");
  } else {
    contraseñaInput.type = "password";
    iconoOjo.classList.remove("fi-sr-eye-crossed");
    iconoOjo.classList.add("fi-sr-eye");
  }
}