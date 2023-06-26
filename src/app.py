import json
import random
import string
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import spacy
import pyttsx3
from flask import Flask, render_template, request, url_for, redirect, session, flash, send_file, send_from_directory
import openai
from flask_mysqldb import MySQL
from config import SECRET, HOSTNAME, USER, PASSWORD, DATABASE
import speech_recognition as sr
from apis import error
from utils.verificacion import enviar_correo
from datetime import datetime, timedelta
from PyPDF2 import PdfReader, PdfWriter
from utils.extraccion import correos
from docx import Document
import traceback
import hashlib
import uuid
from manejoerrores import error100
from datetime import date


app = Flask(__name__)

# Almacenaremos la conexión
app.config['MYSQL_HOST'] = HOSTNAME
app.config['MYSQL_USER'] = USER
app.config['MYSQL_PASSWORD'] = PASSWORD
app.config['MYSQL_DB'] = DATABASE
app.config['SECRET_KEY'] = SECRET
mysql = MySQL(app)

# Configurar la clave de la API de OpenAI


# Cargar modelo de SpaCy en español
nlp = spacy.load('es_core_news_sm')



# Archivo JSON con información contextual
ARCHIVO_CONTEXTUAL = 'contexto.json'



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







# Obtener respuesta utilizando la API de OpenAI
def obtener_respuesta_gpt3(pregunta, key):
    if 'nombre' in session:
        openai.api_key = key
        contexto = cargar_contexto()
        contexto['pregunta'] = pregunta
        guardar_contexto(contexto)
        
        nombre_usuario = session['nombre']
        email_usuario = session['usuario']
        apellido_usuario = session['apellido']
        anos = session['anos']
        anonacimiento = session['AAAA']
        mesnacimiento = session['MM']
        dianacimiento = session['DD']



        datosusuario = f'"(Estos son los datos del usuario, no muestres ni respondas con los datos, a menos que el te lo pida. pero responde todas las preguntas que te hagan.): ", "apellido del usuario:" {apellido_usuario}, "edad del usuario:" {anos}, "ano de nacimiento del usuario:"{anonacimiento}, "mes de nacimiento del usuario"{mesnacimiento}, "dia de nacimiento del usuario"{dianacimiento}, "email del usuario:"{email_usuario}"'

        
        entrada = f'{datosusuario}"nombre"{nombre_usuario}: {pregunta}'
        tokens_entrada = nltk.word_tokenize(entrada)
        
        # Eliminar líneas que comienzan con "Usuario:" y "Bot:"
        codigo_limpio = [linea for linea in tokens_entrada if not linea.startswith(('Usuario:', 'Bot:'))]
        
        # Unir las líneas de código en un solo bloque de texto
        codigo_completo = '\n'.join(codigo_limpio)
        
        # Obtener la respuesta del modelo
        respuesta = openai.Completion.create(
            engine='text-davinci-003',
            prompt=codigo_completo,
            max_tokens=1500,
            n=1,
            stop=None,
            temperature=0.4
        )
        

        nueva_respuesta = respuesta.choices[0].text.strip()
        

        return nueva_respuesta












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
            elif session['datos'] == "NO":
                return redirect(url_for('datos'))
            else:
                return redirect(url_for('index')) 
    elif 'usuario' not in session and request.endpoint not in allowed_routes and not request.path.startswith('/static'):
        return redirect(url_for('home'))



@app.route('/auth/register', methods=["POST", "GET"])
def register():
    try:
        if 'logued' in session and session['logued']:
                    return redirect(url_for('index'))
        if request.method == "POST":
            id_usuario = str(uuid.uuid4())
            nombre = request.form.get('nombre')
            apellido = request.form.get('apellido')
            email = request.form.get('email')
            password = request.form.get('contraseña')
            hashpassword = hashlib.sha256()
            hashpassword.update(password.encode('utf8'))
            hash_value = hashpassword.hexdigest()
            api = request.form.get('openai')
            code = 0
            reason = "NO"
            numeros = ''.join(random.choices(string.digits, k=4))
            cur = mysql.connection.cursor()
            cur.execute("SELECT email from usuarios Where email = %s", (email,))
            user = cur.fetchone()

            try:
                openai.ChatCompletion.create(
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Who won the world series in 2020?"},
                        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
                        {"role": "user", "content": "Where was it played?"}
                    ],
                    model="gpt-3.5-turbo",
                    api_key=api
                )
            except openai.error.AuthenticationError:
                return render_template('auth/register.html', error="La API ingresada es incorrecta",
                                       nombre='', email='', contraseña='', openai='')
            except Exception as e:
                return render_template('auth/register.html', error="Error al verificar la API: " + str(e),
                                       nombre='', email='', contraseña='', openai='')

            if user is None:
                cur1 = mysql.connection.cursor()
                cur1.execute("INSERT INTO verificacion VALUES (%s, %s, %s, %s)",
                             (id_usuario, reason, numeros, datetime.now()))
                cur1.close()

                cur2 = mysql.connection.cursor()
                cur2.execute("INSERT INTO usuarios VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                             (code, id_usuario, nombre, apellido, email, hash_value, api, datetime.now(), reason))
                print(hash_value)
                cur2.close()
                cur3 = mysql.connection.cursor()
                cur3.execute("INSERT INTO preferencias VALUES (%s, %s, %s)",
                             (id_usuario, "TRUE", "TRUE"))
                cur3.close()
                cur4 = mysql.connection.cursor()
                cur4.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
                log = cur4.fetchone()
                session['id'] = log[0]
                session['idgenuine'] = log[1]
                session['nombre'] = log[2]
                session['apellido'] = log[3]
                session['usuario'] = log[4]
                session['api'] = log[6]  # Set the 'api' key in the session dictionary
                session['datos'] = log[8]
                mysql.connection.commit()
                return redirect(url_for('verificacion'))
            else:
                return render_template('auth/register.html', error="El usuario ya existe",
                                       nombre='', email='', contraseña='', openai='')
        else:
            return render_template('auth/register.html')
    except Exception as e:
        traceback.print_exc()
        return render_template('auth/register.html', errorL= error100 ,
                               nombre='', email='', contraseña='', openai='')



# Diccionario para almacenar los intentos de inicio de sesión fallidos por IP
failed_login_attempts = {}

# Diccionario para almacenar las IP bloqueadas y el tiempo en que deben ser desbloqueadas
blocked_ips = {}

# Duración del bloqueo en minutos
bloqueo_duracion_minutos = 30

# Función para verificar si una IP debe ser bloqueada
def check_block_ip(ip):
    if ip in blocked_ips:
        tiempo_desbloqueo = blocked_ips[ip]
        if datetime.now() < tiempo_desbloqueo:
            return True
        else:
            del blocked_ips[ip]
    elif ip in failed_login_attempts and failed_login_attempts[ip] >= 4:
        tiempo_desbloqueo = datetime.now() + timedelta(minutes=bloqueo_duracion_minutos)
        blocked_ips[ip] = tiempo_desbloqueo
        del failed_login_attempts[ip]
        return True
    return False






@app.route('/aboutyou', methods= ['POST', 'GET']) 
def datos():
    try:
            if 'datoscompletos' in session and session['datoscompletos']:
                        return redirect(url_for('index'))
            if request.method == 'POST':
                        idusuario = session['idgenuine']
                        gender = request.form['gender']
                        year = int(request.form['year'])
                        month = int(request.form['month'])
                        day = int(request.form['day'])
                        dob = date(year, month, day)
                        today = date.today()
                        yes = "SI"
                        age = today.year - dob.year
                        if today.month < dob.month:
                             age -= 1
                        elif today.month == dob.month and today.day < dob.day:
                             age -= 1

                        cur = mysql.connection.cursor()
                        cur.execute("INSERT INTO datos VALUES (%s, %s, %s, %s, %s, %s)",
                                    (idusuario, age, year, month, day, gender))
                        cur1 = mysql.connection.cursor()
                        cur1.execute("UPDATE usuarios SET datos = %s WHERE idusuarios = %s",
                                     (yes, idusuario))
                        session['datoscompletos'] = True
                        mysql.connection.commit()
                        cur.close()
                        cur1 = mysql.connection.cursor()
                        cur1.execute("SELECT * FROM datos WHERE idusuarios = %s",
                                     (idusuario,))
                        datos = cur1.fetchone()
                        session['gender'] = datos[1]
                        session['anos'] = datos[2]
                        session['AAAA'] = datos[3]
                        session['MM'] = datos[4]
                        session['DD'] = datos[5]
                        return redirect(url_for('index'))
    except Exception as e:
        traceback.print_exc()
        return render_template('aboutyou.html', errorL = e)
    
    return render_template('aboutyou.html')
        





@app.route('/auth', methods=["POST", "GET"])
def login():
    if 'logued' in session and session['logued']:
        return redirect(url_for('index'))
    if request.method == 'POST':
        try:
            ip = request.remote_addr  # Obtener la IP del cliente
            if check_block_ip(ip):
                flash("Intente de nuevo más tarde.")
                if 'emailsend' not in session:
                    cur2 = mysql.connection.cursor()
                    cur2.execute("SELECT email From usuarios WHERE email = %s", (session['failed_login_attemptsemail'],))
                    email1 = cur2.fetchone()
                    cur2.close()
                    if email1:
                        asunto = "¡Tu cuenta está en peligro!"
                        destinario = session['failed_login_attemptsemail']
                        contenido = """Alguien está intentando acceder a tu cuenta. Si no fuiste tú, debes cambiar tu contraseña lo antes posible.
                        Si fuiste tú y no recuerdas tu contraseña, haz clic en este enlace:
                        http://localhost:5000/auth/resetpassword
                        Si se sigue introduciendo la contraseña incorrecta, nos veremos obligados a bloquear tu cuenta por un tiempo limitado.
                        Gracias. Atentamente, María de Genuine."""
                        enviar_correo(destinario, asunto, contenido)
                        session['emailsend'] = True
                return render_template('auth/login.html')

            usuario = request.form.get('email')
            contraseña = request.form.get('contraseña')
            hashpassword = hashlib.sha256()
            hashpassword.update(contraseña.encode('utf8'))
            hash_value = hashpassword.hexdigest()
            print(hash_value)

            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuarios WHERE email = %s ", (usuario,))
            user = cur.fetchone()
            cur.close()

            if user is not None:
                print("el usuario se encontro en la base de datos")
                contraseñaalma = user[5]
                if hash_value == contraseñaalma:
                    print("La contrasena coincide")
                    session['id'] = user[0]
                    session['idgenuine'] = user[1]
                    session['nombre'] = user[2]
                    session['apellido'] = user[3]
                    session['usuario'] = user[4]
                    session['api'] = user[6]  # Set the 'api' key in the session dictionary
                    session['datos'] = user[8]
                    cur1 = mysql.connection.cursor()
                    cur1.execute("SELECT * FROM verificacion WHERE idusuario = %s", (session['idgenuine'],))
                    verificacion = cur1.fetchone()
                    cur1.close()

                    if verificacion is not None:
                        print("Verificacion se encontro")
                        session['verificado'] = verificacion[1]
                        if session['verificado'] == "NO":
                            print("Verificacion es igual a no")
                            return redirect(url_for('verificacion'))
                        
                        else:
                            if session['datos'] == 'NO':
                                print("Vedatos se encontro")
                                return redirect(url_for('datos'))
                            else:
                                if ip in failed_login_attempts:
                                    print("se chequeo la ip")
                                    del failed_login_attempts[ip]
                                session['logued'] = True
                                cur1 = mysql.connection.cursor()
                                cur1.execute("SELECT * FROM datos WHERE idusuario = %s", (session['idgenuine'],))
                                datos = cur1.fetchone()
                                cur1.close()
                                session['anos'] = datos[1]
                                session['AAAA'] = datos[2]
                                session['MM'] = datos[3]
                                session['DD'] = datos[4]
                                cur3 = mysql.connection.cursor()
                                cur3.execute("SELECT * FROM preferencias WHERE idusuario = %s",
                                             (session['idgenuine'],))
                                preferencias = cur3.fetchone()
                                if preferencias is None:
                                    print("Se encontro pereferencias")
                                    cur4 = mysql.connection.cursor()
                                    cur4.execute("INSERT INTO preferencias VALUES (%s, %s, %s)",
                                                 (session['idgenuine'], "TRUE", "FALSE"))
                                return redirect(url_for('index'))
                    else:
                        return render_template('auth/login.html', error='Usuario o contraseña incorrecto')
                else:
                    # Incrementar el contador de intentos de inicio de sesión fallidos para la IP actual
                    if ip in failed_login_attempts:
                        print("Incremento la ip intentos")
                        failed_login_attempts[ip] += 1
                        session['failed_login_attemptsemail'] = usuario
                    else:
                        failed_login_attempts[ip] = 1

                    # Verificar si se alcanzó el límite de intentos fallidos
                    if failed_login_attempts[ip] >= 4:
                        tiempo_desbloqueo = datetime.now() + timedelta(minutes=bloqueo_duracion_minutos)
                        blocked_ips[ip] = tiempo_desbloqueo
                    print("Verificacion se encontro")
                    return render_template('auth/login.html', error='Usuario o contraseña incorrecto')
            else:
                return render_template('auth/login.html', error='Usuario o contraseña incorrecto')
        except Exception as e:
            traceback.print_exc()
            return render_template('auth/login.html', errorL=error100, email='', contraseña='')
    else:
        return render_template('auth/login.html')










@app.route('/auth/verificacion', methods=["GET", "POST"])
def verificacion():
    try:
        if 'realizadoverificacion' in session and session['realizadoverificacion']:
             return redirect(url_for('index'))
        if request.method == 'POST':
            codigo1 = request.form['code1']
            codigo2 = request.form['code2']
            codigo3 = request.form['code3']
            codigo4 = request.form['code4']
            codigo = codigo1 + codigo2 + codigo3 + codigo4
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM verificacion WHERE idusuario = %s ", (session.get('idgenuine'),))
            codigov = cur.fetchone()
            cur.close()
            if codigov is not None:
                if codigo == codigov[2]:
                    idgenuine = session['idgenuine']
                    cur = mysql.connection.cursor()
                    cur.execute("UPDATE verificacion SET verificado = %s WHERE idusuario = %s", ("SI", idgenuine))
                    mysql.connection.commit()
                    cur.close()
                    session['verificado'] = "SI"
                    session['realizadoverificacion'] = True
                    return redirect(url_for('datos'))
                else:
                    return render_template('auth/verificacion.html', error='Código incorrecto', codigo='', codigo1='', codigo2='', codigo3='', codigo4='')
        else:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM verificacion WHERE idusuario = %s ", (session.get('idgenuine'),))
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

        return redirect(url_for('datos'))

    except Exception as e:
        return render_template('error.html', error=str(e))







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




@app.route('/settings')
def settings():
    return render_template('settings.html')





# Cierre de sesión
@app.route('/salir')
def salir():
    email_usuario = session.get('idgenuine')
    session.clear()
    return redirect(url_for('home'))
# Ruta principal, chat


@app.route('/')
def index():
    nombre = session['nombre']
    principal_mensaje = f"Hola {nombre}, estoy aquí para ayudarte. que deseas hoy?"
    return render_template('chat.html', bienvenida = principal_mensaje)






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








# Convertir texto a voz utilizando pyttsx3
def convertir_texto_a_voz(response):
    idusuario = session['idgenuine']
    engine = pyttsx3.init()

    engine.save_to_file(response, 'respuesta.wav')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM preferencias WHERE idusuario = %s", (idusuario,))
    speak = cur.fetchone()
    if speak is not None:
        hablar = speak[1]
        session['hablar'] = hablar
        if session['hablar'] == "TRUE":
            engine.say(response)
            engine.runAndWait()















@app.route('/get_response', methods=['POST'])
def get_response():
    mensaje = request.form['user_message']
    key = session['api']

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
        try:
            response = obtener_respuesta_gpt3(mensaje, key=key)
            convertir_texto_a_voz(response)
            return response

        except openai.error.AuthenticationError:
            mensaje_error = 'La API ingresada es incorrecta'
            return mensaje_error
        except openai.error.RateLimitError:
            mensaje_error = 'Se ha agotado el límite de solicitudes de la API. Inténtalo más tarde.'
            return mensaje_error
        except Exception as e:
            mensaje_error = 'Ha ocurrido un error: ' + str(e)
            return mensaje_error
        
# Ruta para manejar errores 404
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html')
        


if __name__ == '__main__':


    # Iniciar la aplicación Flask
    app.run(debug=True) 
