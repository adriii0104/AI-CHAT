import os
import json

from flask import Flask, render_template, request
import openai
import nltk
import speech_recognition as sr
import pyttsx3
import subprocess
from config import mi_api

app = Flask(__name__)

openai.api_key = "YOUR_API_KEY"  # Reemplaza con tu clave de API

# Variables globales para el aprendizaje
conversaciones = []

# Archivo para guardar los cambios
ARCHIVO_CAMBIOS = 'cambios.json'

# Cargar conversaciones anteriores y cambios desde el archivo
def cargar_datos():
    global conversaciones
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

# Guardar conversaciones y cambios en el archivo
def guardar_datos():
    with open('conversaciones.json', 'w') as file:
        json.dump(conversaciones, file)

    with open(ARCHIVO_CAMBIOS, 'w') as file:
        json.dump(cambios, file)

# Obtener respuesta utilizando la API de OpenAI
def obtener_respuesta_gpt3(pregunta):
    global conversaciones

    # Verificar si se solicita una modificación en la carpeta
    if pregunta.startswith('modificar carpeta'):
        comando = pregunta.replace('modificar carpeta', '').strip()
        try:
            subprocess.run(comando, shell=True, check=True)
            return 'Carpeta modificada exitosamente'
        except subprocess.CalledProcessError as e:
            return f'Error al modificar la carpeta: {str(e)}'

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

    # Actualizar la conversación con la nueva respuesta
    conversaciones.append((pregunta, nueva_respuesta))

    # Guardar las conversaciones actualizadas en el archivo
    guardar_datos()

    return nueva_respuesta

# Ejecutar código proporcionado
def ejecutar_codigo(codigo):
    try:
        exec(codigo)
        return 'Código ejecutado correctamente'
    except Exception as e:
        return f'Error al ejecutar el código: {str(e)}'

# Ruta principal de la aplicación
@app.route('/')
def home():
    return render_template('chat.html')

# Ruta para procesar las solicitudes del chatbot
@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.form['user_message']
    response_text = obtener_respuesta_gpt3(user_message)

    return response_text

# Ruta para procesar las solicitudes de voz del chatbot
@app.route('/get_voice_response', methods=['POST'])
def get_voice_response():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    user_message = recognizer.recognize_google(audio, language='es')
    response_text = obtener_respuesta_gpt3(user_message)

    return response_text

# Ruta para recibir las instrucciones de modificación del código
@app.route('/modificar_codigo', methods=['POST'])
def modificar_codigo():
    cambios = request.json  # Se espera un JSON con las instrucciones de modificación

    # Verificar si se proporcionaron instrucciones de modificación
    if cambios is None:
        return 'No se proporcionaron instrucciones de modificación'

    # Verificar si el cambio solicitado es válido
    if 'codigo' not in cambios:
        return 'No se proporcionó el cambio de código'

    # Obtener el nuevo código del JSON
    nuevo_codigo = cambios['codigo']

    resultado = ejecutar_codigo(nuevo_codigo)

    return resultado

# Función para borrar un archivo
def borrar_archivo(nombre_archivo):
    try:
        os.remove(nombre_archivo)
        return f"El archivo '{nombre_archivo}' ha sido eliminado exitosamente."
    except OSError as e:
        return f"No se pudo borrar el archivo '{nombre_archivo}'. Error: {str(e)}."

# Ruta para procesar las solicitudes de borrado de archivo
@app.route('/borrar_archivo', methods=['POST'])
def borrar_archivo_route():
    datos = request.json  # Se espera un JSON con el nombre del archivo a borrar

    # Verificar si se proporcionó el nombre del archivo
    if 'nombre_archivo' not in datos:
        return 'No se proporcionó el nombre del archivo a borrar.'

    nombre_archivo = datos['nombre_archivo']
    resultado = borrar_archivo(nombre_archivo)

    return resultado

if __name__ == '__main__':
    nltk.download('punkt')  # Descargar datos necesarios para nltk

    # Cargar conversaciones anteriores y cambios desde el archivo al iniciar la aplicación
    conversaciones, cambios = cargar_datos()

    # Actualizar el código del archivo
    with open(__file__, 'r') as file:
        codigo_actual = file.read()
    cambios['codigo'] = codigo_actual

    # Guardar los cambios en el archivo
    guardar_datos()

    app.run(debug=True)
