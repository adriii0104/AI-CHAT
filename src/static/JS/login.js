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
function validate() {
  let email = document.getElementById("email").value;
  let password = document.getElementById("contraseña").value;
  var button = document.getElementById("button");
  let emailvalid = /^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i;


  const isFormValid = email.length >= 7 && password.length >= 7 && emailvalid.test(email);

  button.disabled = !isFormValid;
  button.style.color = isFormValid ? "white" : "#969696b0";
  button.style.backgroundColor = isFormValid ? "black" : "#96969631";
  button.style.cursor = isFormValid ? "pointer" : "default";
  console.log(isFormValid ? "button enabled" : "button disabled");
  
}  