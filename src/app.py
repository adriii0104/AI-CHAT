import json
import random
import string
import nltk
import spacy
import pyttsx3
from flask import Flask, render_template, request, url_for, redirect, session, flash, send_file, send_from_directory
import openai
from sklearn.feature_extraction.text import CountVectorizer
from flask_mysqldb import MySQL
from config import mi_api, SECRET
import speech_recognition as sr
from apis import error
from utils.verificacion import enviar_correo
from datetime import datetime, timedelta
from PyPDF2 import PdfReader, PdfWriter
from utils.extraccion import correos
from docx import Document
import os


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
            max_tokens=1500,
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





@app.route('/work/pdf', methods=['POST'])
def work_pdf():
    # Obtener el contenido de la solicitud
    content = request.form['content']

    # Crear un nuevo archivo PDF
    pdf = PdfWriter()
    pdf.add_page()
    pdf.add_text(10, 10, content)

    # Guardar el archivo PDF en un archivo temporal
    temp_file = 'c:\\Users\\El bobul\\Desktop\\IA\\temp.docx'
    with open(temp_file, 'wb') as file:
        pdf.write(file)

    # Generar el enlace de descarga
    download_link = url_for('download_file', filename=temp_file)

    # Redirigir al cliente a la ruta de descarga
    print(download_link)






@app.route('/work/word', methods=['POST'])
def work_word():
    print("Antes de crear el documento Word")
    # Obtener el contenido de la solicitud
    content = request.form.get('content')
    print(content)

    # Crear un nuevo documento Word
    doc = Document()
    doc.add_paragraph(content)

    # Guardar el documento en un archivo temporal
    temp_file = 'c:\\Users\\El bobul\\Desktop\\IA\\temp.docx'
    doc.save(temp_file)
    
    print("Después de crear el documento Word")

    return send_file()











@app.route('/download', methods=['GET'])
def download_file():
    # Obtener el nombre del archivo a descargar
    filename = request.args.get('filename')

    # Devolver el archivo como respuesta
    return send_file(filename, as_attachment=True)













# Estos son los corredores, ej. login, register, chat, etc.




























@app.before_request
def before_request():
    allowed_routes = ['login', 'register', 'home']
    if 'usuario' in session and request.endpoint in allowed_routes:
            if session['verificado'] == "NO":
                return redirect(url_for('verificacion'))
            else:
               return redirect(url_for('index'))
    elif 'usuario' not in session and request.endpoint not in allowed_routes and not request.path.startswith('/static'):
        return redirect(url_for('home'))










# Registro
@app.route('/auth/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
            nombre = request.form.get('nombre')
            email = request.form.get('email')
            password = request.form.get('contraseña')
            code = 0
            reason = "NO"
            numeros = ''.join(random.choices(string.digits, k=4))
            codigo = "BLID" + numeros
            cur1 = mysql.connection.cursor()
            cur1.execute("SELECT usuario from usuarios Where usuario = %s", (email, ))
            user = cur1.fetchone()
            if user is None:

                cur1 = mysql.connection.cursor()
                cur1.execute("INSERT INTO verificacion VALUES (%s, %s, %s, %s)",
                             (codigo, reason, numeros, datetime.now()))
                
                cur1.close()

                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO usuarios VALUES (%s, %s, %s, %s, %s)",
                             (code, codigo, nombre, email, password))
                
                mysql.connection.commit()

                return redirect(url_for('login'))
            else:
                return render_template('auth/register.html', error=error)
    else:
        return render_template('auth/register.html')



# Login
# Login
@app.route('/auth', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        usuario = request.form['email']
        contraseña = request.form['contraseña']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE usuario = %s ", (usuario,))
        user = cur.fetchone()
        cur.close()

        if user is not None:
            contraseñaalma = user[4]
            if contraseña == contraseñaalma:
                session['id'] = user[0]
                session['idgenuine'] = user[1]
                session['nombre'] = user[2]
                session['usuario'] = user[3]

                cur1 = mysql.connection.cursor()
                cur1.execute("SELECT * FROM verificacion WHERE idblid = %s ", (session['idgenuine'],))
                verificacion = cur1.fetchone()
                cur1.close()

                if verificacion is not None:
                    session['verificado'] = verificacion[1]
                    if session['verificado'] == "NO":
                        return redirect(url_for('verificacion'))
                    else:
                        return redirect(url_for('index'))
                else:
                    return render_template('auth/login.html', error='Usuario o contraseña incorrecto')
            else:
                return render_template('auth/login.html', error='Usuario o contraseña incorrecto')
        else:
            return render_template('auth/login.html', error='Usuario o contraseña incorrecto')
    else:
        return render_template('auth/login.html')








@app.route('/auth/verificacion', methods=["GET", "POST"])
def verificacion():
    if request.method == 'POST':
        codigo = request.form['codigo']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM verificacion WHERE idblid = %s ", (session.get('idgenuine'),))
        codigov = cur.fetchone()
        cur.close()
        if codigov is not None:
            if codigo == codigov[2]:
                idgenuine = session['idgenuine']
                cur = mysql.connection.cursor()
                cur.execute("UPDATE verificacion SET verificado = %s WHERE idblid = %s", ("SI", idgenuine))
                mysql.connection.commit()
                cur.close()
                session['verificado'] = "SI"
                return redirect(url_for('index'))
            else:
                return render_template('auth/verificacion.html', error='Código incorrecto')
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM verificacion WHERE idblid = %s ", (session.get('idgenuine'),))
        code = cur.fetchone()
        cur.close()
        if code is None or code[2] is None:
            return render_template('auth/verificacion.html', error='No se encontró ningún código')
        else:
            destinatario = session.get('usuario')
            asunto = 'Tu código de verificación Genuine'
            contenido = 'Aquí está tu código de verificación de Genuine: {}'
            
            # Verificar si ya se envió un código de verificación antes
            if 'codigo_enviado' not in session:
                enviar_correo(destinatario, asunto, contenido.format(code[2]))
                session['codigo_enviado'] = True  # Establecer la bandera de código enviado
            
        return render_template('auth/verificacion.html')

    return redirect(url_for('index'))






@app.route('/auth/verificacion/resend')
def resend():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM verificacion WHERE idblid = %s", (session.get('idgenuine'),))
    code = cur.fetchone()
    cur.close()

    if code is not None and code[2] is not None:
        nuevo_codigo = ''.join(random.choices(string.digits, k=4))
        destinatario = session.get('usuario')
        idgenuine = session.get('idgenuine')
        cur1 = mysql.connection.cursor()
        cur1.execute("UPDATE verificacion SET codigo = %s WHERE idblid = %s",
        (nuevo_codigo, idgenuine))
        mysql.connection.commit()
        cur1.close()
        asunto = 'Tu código de verificación Genuine'
        contenido = 'Aquí está tu nuevo código de verificación de Genuine: {}'
        contenido = contenido.format(nuevo_codigo)
        enviar_correo(destinatario, asunto, contenido)
        
        
        # Redireccionar a la vista actual en lugar de 'verificacion'
        return redirect(url_for('verificacion', error = "Se ha enviado un nuevo codigo de verificacion"))
    else:
        return render_template('auth/verificacion.html', error='No se encontró ningún código')










# Cierre de sesión
@app.route('/salir')
def salir():
    session.clear()
    return redirect(url_for('home'))

# Ruta principal, chat
@app.route('/')
def index():
    return render_template('chat.html')


@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/read/pdf', methods=['GET', 'POST'])
def read_pdf():
    if request.method == 'POST':
        pdf = request.files['pdf_file']
        # Guarda el archivo PDF en el servidor
        pdf.save("uploaded.pdf")
        
        reader = PdfReader("uploaded.pdf")
        number_of_pages = len(reader.pages)
        page = reader.pages[0]
        text = page.extract_text()
        
        return render_template('read.html', text=text)
    
    return render_template('upload.html')












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

    if mensaje.startswith('word:'):
        # Solicitar un trabajo en Word
        content = mensaje[5:].strip()
        return redirect(url_for('work_word', content=content))
    elif mensaje.startswith('pdf:'):
        # Solicitar un trabajo en PDF
        content = mensaje[4:].strip()
        return redirect(url_for('work_pdf', content=content))
    else:
        # Obtener respuesta del modelo GPT-3
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
