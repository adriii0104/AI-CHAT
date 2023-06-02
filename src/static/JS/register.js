function validate() {
  let nombre = document.getElementById("nombre").value;
  let email = document.getElementById("email").value;
  let password = document.getElementById("contraseña").value;
  let confirmPassword = document.getElementById("ccontraseña").value;
  var button = document.getElementById("button");
  let emailvalid = /^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i;

  const isFormValid = nombre.length >= 7 && email.length >= 7 && password.length >= 7 && confirmPassword.length >= 7 && emailvalid.test(email);

  button.disabled = !isFormValid;
  button.style.color = isFormValid ? "white" : "#969696b0";
  button.style.backgroundColor = isFormValid ? "black" : "#96969631";
  button.style.cursor = isFormValid ? "pointer" : "default";
  console.log(isFormValid ? "button enabled" : "button disabled");
}

function check() {
  let password = document.getElementById("contraseña");
  let confirmPassword = document.getElementById("ccontraseña");
  let error = document.getElementById("error-email");

  if (password.value !== confirmPassword.value) {
    password.value = "";
    confirmPassword.value = "";
    password.style.border = "1px solid red";
    confirmPassword.style.border = "1px solid red";
    button.style.color = "rgba(150, 150, 150, 0.69)";
    button.style.backgroundColor = "rgba(150, 150, 150, 0.192)"
    button.style.borderColor = "#0000";
    button.style.cursor = "not-allowed";
    error.style.color = "red";

    error.innerHTML = "Las contraseñas no coinciden";
    return false;
  } else {
    error.innerHTML = "";
    return true;
  }
}
if (condition) {
  
}