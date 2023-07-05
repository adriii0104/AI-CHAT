// scripts.js
var recognition;
var isListening = false;

function startListening() {
    if (isListening) {
        recognition.stop();
        return;
    }

    recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;

    recognition.onstart = function() {
        document.getElementById("audio-btn").classList.add("listening");
        isListening = true;
    };

    recognition.onresult = function(event) {
        var result = event.results[event.results.length - 1][0].transcript;
        document.getElementById("user-input").classList.add("listening");
        document.getElementById("user-message").value = result;
        sendMessage();
    };

    recognition.onend = function() {
        document.getElementById("audio-btn").classList.remove("listening");
        document.getElementById("user-input").classList.remove("listening");
        isListening = false; // Reiniciar la variable isListening a false
    };

    recognition.start();
}

function sendMessage() {
    var userMessage = document.getElementById("user-message").value;
    var messageList = document.getElementById("message-list");

    // Agregar el mensaje del usuario a la lista de mensajes
    var userMessageItem = document.createElement("li");
    userMessageItem.classList.add("user-message");
    userMessageItem.textContent = "Tú: " + userMessage;
    messageList.appendChild(userMessageItem);

    // Agregar animación de escritura al mensaje del chatbot
    var typingAnimation = document.createElement("span");
    typingAnimation.classList.add("typing-animation");
    typingAnimation.textContent = "Corin Bot: ";
    var chatbotMessageItem = document.createElement("li");
    chatbotMessageItem.classList.add("chatbot-message");
    chatbotMessageItem.appendChild(typingAnimation);
    messageList.appendChild(chatbotMessageItem);

    // Enviar el mensaje al servidor para obtener la respuesta
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = this.responseText;

            // Remover animación de escritura
            chatbotMessageItem.removeChild(typingAnimation);

            // Agregar la respuesta del chatbot a la lista de mensajes
            var chatbotResponseItem = document.createElement("span");
            chatbotResponseItem.textContent = response;
            chatbotMessageItem.appendChild(chatbotResponseItem);

            // Limpiar el campo de entrada de usuario
            document.getElementById("user-message").value = "";

            // Desplazarse al final de la lista de mensajes
            messageList.scrollTop = messageList.scrollHeight;
        }
    };

    // Enviar el mensaje de texto al servidor
    xhttp.open("POST", "/get_response", true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.send("user_message=" + userMessage);
}

document.getElementById("user-message").addEventListener("keydown", function(event) {
    if (event.keyCode === 13) { // Código de tecla 13 corresponde a "Enter"
        event.preventDefault(); // Evitar que se agregue un salto de línea en el textarea
        sendMessage(); // Llamar a la función sendMessage()
    }
});



const messageList = document.getElementById('message-list');
const userMessageInput = document.getElementById('user-message');

// Función para enviar un mensaje al chat
function sendMessage() {
    const userMessage = userMessageInput.value.trim();

    if (userMessage !== '') {
        addUserMessage(userMessage);
        userMessageInput.value = '';
        sendRequest(userMessage);
    }
}

// Función para agregar un mensaje del usuario al chat
function addUserMessage(message) {
    const userMessageItem = createMessageItem(message, 'user-message');
    messageList.appendChild(userMessageItem);
    scrollToBottom();
}

// Función para agregar un mensaje del bot al chat
function addBotMessage(message) {
    const botMessageItem = createMessageItem(message, 'bot-message');
    messageList.appendChild(botMessageItem);
    scrollToBottom();
}

// Función para agregar un mensaje de voz al chat
function addVoiceMessage(message) {
    const voiceMessageItem = createMessageItem(message, 'voice-message');
    messageList.appendChild(voiceMessageItem);
    scrollToBottom();
}

// Función para crear un elemento de mensaje
function createMessageItem(message, className) {
    const messageItem = document.createElement('li');
    messageItem.className = `message ${className}`;
    const messageContent = document.createElement('p');
    messageContent.className = 'message-content';
    messageContent.textContent = message;
    messageItem.appendChild(messageContent);
    return messageItem;
}

// Función para hacer una solicitud al chatbot
function sendRequest(message) {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/get_response', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            const response = xhr.responseText;
            addBotMessage(response);
            speakResponse(response);
        }
    };
    xhr.send(`user_message=${encodeURIComponent(message)}`);
}

// Función para hablar la respuesta del bot
function speakResponse(response) {
    const utterance = new SpeechSynthesisUtterance(response);
    utterance.lang = 'es';
    speechSynthesis.speak(utterance);
}

// Función para desplazarse hasta el fondo del chat
function scrollToBottom() {
    messageList.scrollTop = messageList.scrollHeight;
}


