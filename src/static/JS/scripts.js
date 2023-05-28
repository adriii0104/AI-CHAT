// scripts.js
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
