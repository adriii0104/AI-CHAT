from flask import Flask, render_template, request
import openai
import nltk
from nltk.chat.util import Chat, reflections
import requests
from bs4 import BeautifulSoup
import speech_recognition as sr
import pyttsx3

app = Flask(__name__)

# Configurar la clave de la API de OpenAI
openai.api_key = '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'

# Definir los patrones de entrada y respuestas
pares = [
    [
        r"(.*) resolver (.*)",
        ["Déjame ayudarte a resolver ese problema. Por favor, proporciona más detalles o el código que necesitas resolver."]
    ],
    [
        r"(.*) buscar (.*)",
        ["Permíteme buscar información relacionada con '%2'..."]
    ],
    [
        r"(.*)",
        ["Lo siento, no puedo resolver ese problema en particular. ¿Hay algo más en lo que pueda ayudarte?"]
    ]
]

# Crear un Chatbot
def crear_chatbot():
    chatbot = Chat(pares, reflections)
    return chatbot

# Obtener respuesta utilizando la API de OpenAI
def obtener_respuesta_gpt3(pregunta):
    respuesta = openai.Completion.create(
        engine='text-davinci-003',
        prompt=pregunta,
        max_tokens=1100,
        n=1,
        stop=None,
        temperature=0.7
    )
    return respuesta.choices[0].text.strip()

# Convertir texto a voz
def convertir_texto_a_voz(texto):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Velocidad de reproducción de voz
    engine.setProperty('volume', 0.8)  # Volumen de voz
    engine.say(texto)
    engine.runAndWait()

# Ruta principal de la aplicación
@app.route('/')
def home():
    return render_template('chat.html')

# Ruta para procesar las solicitudes del chatbot
@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.form['user_message']
    chatbot = crear_chatbot()

    response = obtener_respuesta_gpt3(user_message)

    # Convertir la respuesta de texto a voz
    convertir_texto_a_voz(response)

    return response

# Ruta para procesar las solicitudes de voz del chatbot
@app.route('/get_voice_response', methods=['POST'])
def get_voice_response():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    user_message = recognizer.recognize_google(audio, language='es')
    chatbot = crear_chatbot()

    if "buscar" in user_message:
        query = user_message.split("buscar ")[1]
        response = buscar_en_linea(query)
    else:
        response = obtener_respuesta_gpt3(user_message)

    # Convertir la respuesta de texto a voz
    convertir_texto_a_voz(response)

    return response

if __name__ == '__main__':
    nltk.download('punkt')  # Descargar datos necesarios para nltk
    app.run(debug=True)
