import json
import nltk
import spacy
import pickle
from flask import Flask, render_template, request
import openai
from sklearn.feature_extraction.text import CountVectorizer
import pyttsx3
from config import mi_api

app = Flask(__name__)

# Configurar la clave de la API de OpenAI
openai.api_key = mi_api

# Cargar modelo de SpaCy en español
nlp = spacy.load('es_core_news_sm')

# Archivo JSON con información contextual
ARCHIVO_CONTEXTUAL = 'contexto.json'
ARCHIVO_CAMBIOS = 'cambios.json'

# Crear archivos necesarios si no existen
def crear_archivos():
    archivos = [ARCHIVO_CONTEXTUAL, ARCHIVO_CAMBIOS]

    for archivo in archivos:
        try:
            with open(archivo, 'r') as f:
                pass
        except FileNotFoundError:
            with open(archivo, 'w') as f:
                json.dump({}, f)

# Cargar información contextual desde el archivo JSON
def cargar_contexto():
    try:
        with open(ARCHIVO_CONTEXTUAL, 'r') as file:
            contexto = json.load(file)
    except FileNotFoundError:
        contexto = {}

    return contexto

# Guardar información contextual en el archivo JSON
def guardar_contexto(contexto):
    with open(ARCHIVO_CONTEXTUAL, 'w') as file:
        json.dump(contexto, file)

# Cargar datos previos desde el archivo
def cargar_datos():
    try:
        with open('conversaciones.json', 'r') as file:
            conversaciones = json.load(file)
    except FileNotFoundError:
        conversaciones = []

    try:
        with open(ARCHIVO_CAMBIOS, 'r') as file:
            cambios = json.load(file)
    except FileNotFoundError:
        cambios = {}

    return conversaciones, cambios

# Guardar datos en los archivos correspondientes
def guardar_datos(conversaciones, cambios):
    with open('conversaciones.json', 'w') as file:
        json.dump(conversaciones, file)

    with open(ARCHIVO_CAMBIOS, 'w') as file:
        json.dump(cambios, file)

# Obtener respuesta utilizando la API de OpenAI
def obtener_respuesta_gpt3(pregunta):
    global conversaciones, cambios

    # Cargar información contextual
    contexto = cargar_contexto()
    contexto['pregunta'] = pregunta
    guardar_contexto(contexto)

    conversacion_actual = conversaciones + [(pregunta, '')]
    entrada = '\n'.join(f'Usuario: {user}\nBot: {bot}' for user, bot in conversacion_actual)
    respuesta = openai.Completion.create(
        engine='text-davinci-003',
        prompt=entrada,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7
    )
    nueva_respuesta = respuesta.choices[0].text.strip()

    # Agregar la nueva respuesta al cerebro de conversaciones sin consumir todos los tokens
    if len(conversaciones) > 0:
        tokens_cerebro = sum(len(nltk.word_tokenize(bot)) for _, bot in conversaciones)
        tokens_nueva_respuesta = len(nltk.word_tokenize(nueva_respuesta))
        if tokens_cerebro + tokens_nueva_respuesta <= 4096:  # Límite máximo de tokens
            conversaciones.append((pregunta, nueva_respuesta))

    # Guardar cambios en el archivo
    guardar_datos(conversaciones, cambios)

    return nueva_respuesta

# Realizar aprendizaje activo para mejorar las respuestas
def aprendizaje_activo(pregunta, respuesta):
    global cambios

    if pregunta.strip() == '':
        return

    if respuesta.strip() == '':
        return

    # Tokenizar la pregunta
    tokenizer = CountVectorizer().build_tokenizer()
    tokens = tokenizer(pregunta.lower())

    # Realizar aprendizaje activo solo si la pregunta tiene más de 3 palabras
    if len(tokens) <= 3:
        return

    # Agregar la pregunta y su respuesta al diccionario de cambios
    cambios[pregunta.lower()] = respuesta

    # Guardar cambios en el archivo
    guardar_datos(conversaciones, cambios)

# Convertir texto a voz utilizando pyttsx3
def convertir_texto_a_voz(texto):
    engine = pyttsx3.init()
    engine.save_to_file(texto, 'respuesta.wav')
    engine.runAndWait()

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    mensaje = request.form['user_message']
    response = obtener_respuesta_gpt3(mensaje)

    # Realizar aprendizaje activo
    aprendizaje_activo(mensaje, response)

    # Convertir la respuesta de texto a voz
    convertir_texto_a_voz(response)

    return response

if __name__ == '__main__':
    crear_archivos()

    # Cargar datos previos
    conversaciones, cambios = cargar_datos()

    # Iniciar la aplicación Flask
    app.run(debug=True)
