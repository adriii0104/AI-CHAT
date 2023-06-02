function togglePasswordVisibility() {
    var contraseñaInput = document.getElementById("contraseña");
    var iconoOjos = document.querySelectorAll(".fi-sr-eye");
  
    if (contraseñaInput.type === "password") {
      contraseñaInput.type = "text";
      iconoOjos[0].classList.remove("fi-sr-eye");
      iconoOjos[0].classList.add("fi-sr-eye-crossed");
    } else {
      contraseñaInput.type = "password";
      iconoOjos[0].classList.remove("fi-sr-eye-crossed");
      iconoOjos[0].classList.add("fi-sr-eye");
    }
  }
  