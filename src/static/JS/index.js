function showSpinner(button) {
    // Crear el elemento del spinner
    var spinner = document.createElement('span');
    spinner.classList.add('spinner');
  
    // Reemplazar el contenido del botón con el spinner
    button.innerHTML = '';
    button.appendChild(spinner);
  
    // Mostrar el spinner cambiando el valor de display
    spinner.style.display = 'inline-block';
    window.location.href = 'http://127.0.0.1:5000/auth/register';
  
    // Redirigir después de mostrar el spinner
  }
      document.addEventListener("DOMContentLoaded", function(event) {
          var textElements = document.getElementsByClassName("texto");
          var delay = 20000; // Retraso en milisegundos entre la aparición y desaparición de cada texto
          var currentIndex = 0;
  
          function showNextText() {
              if (currentIndex < textElements.length) {
                  textElements[currentIndex].style.display = "block";
                  setTimeout(function() {
                      textElements[currentIndex].style.display = "none";
                      currentIndex++;
                      showNextText();
                  }, delay);
              }
          }
  
          showNextText();
      });
  