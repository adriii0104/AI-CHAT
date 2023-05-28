import json
import nltk
import spacy
import pyttsx3
from flask import Flask, render_template, request, url_for, redirect, session
import openai
from sklearn.feature_extraction.text import CountVectorizer
from flask_mysqldb import MySQL
from config import mi_api, SECRET
import speech_recognition as sr


app = Flask(__name__)

# Almacenaremos la conexión
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ia'
app.config['SECRET_KEY'] = SECRET
mysql = MySQL(app)

# Configurar la clave de la API de OpenAI
openai.api_key = mi_api

# Cargar modelo de SpaCy en español
nlp = spacy.load('es_core_news_sm')

# Archivo JSON con información contextual
ARCHIVO_CONTEXTUAL = 'contexto.json'
ARCHIVO_CONVERSACIONES = 'conversaciones.json'

# Crear archivos necesarios si no existen
def crear_archivos():
    archivos = [ARCHIVO_CONTEXTUAL, ARCHIVO_CONVERSACIONES]

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

# Cargar conversaciones desde el archivo JSON
def cargar_conversaciones():
    try:
        with open(ARCHIVO_CONVERSACIONES, 'r') as file:
            conversaciones = json.load(file)
    except FileNotFoundError:
        conversaciones = {}

    return conversaciones

# Guardar conversaciones en el archivo JSON
def guardar_conversaciones(conversaciones):
    with open(ARCHIVO_CONVERSACIONES, 'w') as file:
        json.dump(conversaciones, file)

# Obtener respuesta utilizando la API de OpenAI
def obtener_respuesta_gpt3(pregunta, conversaciones):
    # Cargar información contextual
    contexto = cargar_contexto()
    contexto['pregunta'] = pregunta
    guardar_contexto(contexto)

    conversaciones_list = [(key, value) for key, value in conversaciones.items()]
    conversacion_actual = conversaciones_list + [(pregunta, '')]
    entrada = '\n'.join(f'Usuario: {user}\nBot: {bot}' for user, bot in conversacion_actual)
    tokens_entrada = nltk.word_tokenize(entrada)

    # Dividir la entrada en partes más pequeñas para reducir los gastos de tokens
    partes_entrada = []
    inicio = 0
    while inicio < len(tokens_entrada):
        fin = min(inicio + 4096, len(tokens_entrada))
        partes_entrada.append(' '.join(tokens_entrada[inicio:fin]))
        inicio = fin

    # Obtener respuestas para cada parte de la entrada
    respuestas = []
    for parte_entrada in partes_entrada:
        respuesta = openai.Completion.create(
            engine='text-davinci-003',
            prompt=parte_entrada,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.7
        )
        nueva_respuesta = respuesta.choices[0].text.strip()
        respuestas.append(nueva_respuesta)

    # Combinar todas las respuestas
    nueva_respuesta = ' '.join(respuestas)

    # Agregar la nueva respuesta al cerebro de conversaciones sin consumir todos los tokens
    if len(conversaciones) > 0:
        tokens_cerebro = sum(len(nltk.word_tokenize(bot)) for _, bot in conversaciones.items())
        tokens_nueva_respuesta = len(nltk.word_tokenize(nueva_respuesta))
        if tokens_cerebro + tokens_nueva_respuesta <= 4096:  # Límite máximo de tokens
            conversaciones[pregunta] = nueva_respuesta

    return nueva_respuesta

# Realizar aprendizaje activo para mejorar las respuestas
def aprendizaje_activo(pregunta, respuesta, cambios):
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
    guardar_conversaciones(cambios)

# Convertir texto a voz utilizando pyttsx3
def convertir_texto_a_voz(texto):
    engine = pyttsx3.init()
    engine.save_to_file(texto, 'respuesta.wav')
    engine.runAndWait()

# Estos son los corredores, ej. login, register, chat, etc.

@app.before_request
def before_request():
    allowed_routes = ['login', 'register']
    if 'usuario' in session and request.endpoint in allowed_routes:
        return redirect(url_for('index'))
    elif 'usuario' not in session and request.endpoint not in allowed_routes and not request.path.startswith('/static'):
        return redirect(url_for('login'))

# Registro
@app.route('/auth/register')
def register():
    return render_template('auth/register.html')

# Login
@app.route('/auth', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE usuario = %s ", (usuario,))
        user = cur.fetchone()
        cur.close()
        if user is not None:
            contraseñaalma = user[1]
            if contraseña == contraseñaalma:
                session['usuario'] = user[0]
                return redirect(url_for('index'))
            else:
                return render_template('auth/login.html', error='Usuario o contraseña incorrecto')
        else:
            return render_template('auth/login.html', error='Usuario o contraseña incorrecto')
    else:
        return render_template('auth/login.html')

# Cierre de sesión
@app.route('/salir')
def salir():
    session.clear()
    return redirect(url_for('login'))

# Ruta principal, chat
@app.route('/')
def index():
    return render_template('chat.html')







@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    # Obtener el archivo de audio enviado por el cliente
    audio_file = request.files['audio']

    # Crear un reconocedor de voz
    recognizer = sr.Recognizer()

    try:
        # Leer el archivo de audio utilizando SpeechRecognition
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)

        # Realizar el reconocimiento de voz
        text = recognizer.recognize_google(audio_data, language='es-ES')

        # Devolver el texto reconocido como respuesta
        return text
    except Exception as e:
        # Manejar cualquier error que ocurra durante el reconocimiento de voz
        return str(e)














# Ruta para las respuestas
@app.route('/get_response', methods=['POST'])
def get_response():
    mensaje = request.form['user_message']
    conversaciones = cargar_conversaciones()
    response = obtener_respuesta_gpt3(mensaje, conversaciones)

    # Realizar aprendizaje activo
    aprendizaje_activo(mensaje, response, conversaciones)

    # Guardar conversaciones actualizadas
    guardar_conversaciones(conversaciones)

    # Convertir la respuesta de texto a voz
    convertir_texto_a_voz(response)

    return response

if __name__ == '__main__':
    crear_archivos()

    # Cargar datos previos
    cambios = cargar_conversaciones()

    # Iniciar la aplicación Flask
    app.run(debug=True)
