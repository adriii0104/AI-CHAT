function check() {
  var check = document.getElementById("checkbox");
  if (check.checked) {
    document.getElementById("password").type = "text";
      } else {
        document.getElementById("password").type = "password";
}
}

function validate() {
  let email = document.getElementById("email").value;
  let password = document.getElementById("password").value;
  var button = document.getElementById("button");
  let emailvalid = /^(([^<>()[\]\.,;:\s@\"]+(\.[^<>()[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i;


  const isFormValid = email.length >= 7 && password.length >= 7 && emailvalid.test(email);

  button.disabled = !isFormValid;
  button.style.color = isFormValid ? "black" : "#969696b0";
  button.style.backgroundColor = isFormValid ? "white" : "#96969631";
  button.style.cursor = isFormValid ? "pointer" : "default";
  
}
document.getElementById('button').addEventListener('click', function() {
  showSpinner(this);
});

function showSpinner(button) {
  // Crear el elemento del spinner
  var spinner = document.createElement('span');
  spinner.classList.add('spinner');

  // Reemplazar el contenido del botón con el spinner
  button.innerHTML = '';
  button.appendChild(spinner);

  // Mostrar el spinner cambiando el valor de display
  spinner.style.display = 'inline-block';

}