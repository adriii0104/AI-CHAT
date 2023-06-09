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
import traceback
import hashlib
import uuid

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

# Crear archivos necesarios si no existen
def crear_archivos(email_usuario):
    carpeta_usuario = "archivos_usuario"
    archivo_conversaciones = f"{email_usuario}.json"
    archivos = [ARCHIVO_CONTEXTUAL, archivo_conversaciones]
    
    # Crea la carpeta si no existe
    if not os.path.exists(carpeta_usuario):
        os.makedirs(carpeta_usuario)
    
    for archivo in archivos:
        ruta_archivo = os.path.join(carpeta_usuario, archivo)
        try:
            with open(ruta_archivo, 'r') as f:
                pass
        except FileNotFoundError:
            with open(ruta_archivo, 'w') as f:
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
        print(contexto)
        json.dump(contexto, file)

# Cargar conversaciones desde el archivo JSON
def cargar_conversaciones(email_usuario):
    if 'usuario' in session:
        archivo_conversaciones = f"{email_usuario}.json"
        with open(archivo_conversaciones, 'r') as file:
            conversaciones = json.load(file)
            return conversaciones
    else:
        # Manejar el caso cuando no se encuentra el usuario en la sesión
        return []



# Guardar conversaciones en el archivo JSON
def guardar_conversaciones(email_usuario, conversaciones):
    if 'usuario' in session:
        archivo_conversaciones = f"{email_usuario}.json"
        try:
            with open(archivo_conversaciones, 'r') as file:
                conversaciones_previas = json.load(file)
        except FileNotFoundError:
            conversaciones_previas = []  # Si el archivo no existe, crear una nueva lista de conversaciones

        if isinstance(conversaciones, list):
            conversaciones_previas.append(conversaciones)  # Agregar las nuevas conversaciones a la lista previa

        try:
            with open(archivo_conversaciones, 'w') as file:
                json.dump(conversaciones_previas, file)
        except Exception as e:
            traceback.print_exc()  # Imprimir la traza de error



# Obtener respuesta utilizando la API de OpenAI
def obtener_respuesta_gpt3(pregunta, conversaciones):
    if 'usuario' in session:
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


    return nueva_respuesta







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
            id_usuario = str(uuid.uuid4())
            nombre = request.form.get('nombre')
            email = request.form.get('email')
            password = request.form.get('contraseña')
            hashpassword = hashlib.sha256()
            hashpassword.update(password.encode('utf8'))
            hash_value = hashpassword.hexdigest()
            Hashapi = request.form.get('openai')
            code = 0
            reason = "NO"
            numeros = ''.join(random.choices(string.digits, k=4))
            cur1 = mysql.connection.cursor()
            cur1.execute("SELECT usuario from usuarios Where usuario = %s", (email, ))
            user = cur1.fetchone()
            if user is None:

                cur1 = mysql.connection.cursor()
                cur1.execute("INSERT INTO verificacion VALUES (%s, %s, %s, %s)",
                             (id_usuario, reason, numeros, datetime.now()))
                
                cur1.close()

                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO usuarios VALUES (%s, %s, %s, %s, %s, %s)",
                             (code, id_usuario, nombre, email, hash_value, Hashapi))
                
                mysql.connection.commit()

                flash("Felicidades, ya casi eres parte de Genuine. Inicia Sesión por seguridad.")
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
        contraseñahasheada = hashlib.sha256()
        contraseñahasheada.update(contraseña.encode('utf8'))
        hash_ingresada = contraseñahasheada.hexdigest()

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE usuario = %s ", (usuario,))
        user = cur.fetchone()
        cur.close()

        if user is not None:
            contraseñaalma = user[4]
            if hash_ingresada == contraseñaalma:  # Comparar el hash ingresado con el hash almacenado
                session['id'] = user[0]
                session['idgenuine'] = user[1]
                session['nombre'] = user[2]
                session['usuario'] = user[3]
                email_usuario = session['usuario']
                crear_archivos(email_usuario)

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

                # Crear el archivo JSON para el usuario
                email_usuario = session['idgenuine']
                archivo_usuario = f"{email_usuario}.json"
                if not os.path.exists(archivo_usuario):
                    with open(archivo_usuario, 'w') as f:
                        json.dump({}, f)

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
    email_usuario = session.get('idgenuine')
    conversaciones = cargar_conversaciones(email_usuario)
    guardar_conversaciones(email_usuario, conversaciones)
    session.clear()
    return redirect(url_for('home'))
# Ruta principal, chat
@app.route('/')
def index():
    email_usuario = session.get('idgenuine')
    conversaciones = cargar_conversaciones(email_usuario)
    return render_template('chat.html', conversaciones=conversaciones)


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
    email_usuario = session['idgenuine']

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
        conversaciones = cargar_conversaciones(email_usuario)
        response = obtener_respuesta_gpt3(mensaje, conversaciones)
        guardar_conversaciones(email_usuario, conversaciones)
        print(conversaciones)
        return response

        # Guardar conversaciones actualizadas


if __name__ == '__main__':

    # Iniciar la aplicación Flask
    app.run(debug=True) 
