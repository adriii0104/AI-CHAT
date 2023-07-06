import json
import random
import string
import spacy
import pyttsx3
from flask import Flask, render_template, request, url_for, redirect, session, flash, send_file, make_response
import openai
from flask_mysqldb import MySQL
from config import SECRET, HOSTNAME, USER, PASSWORD, DATABASE
from utils.verificacion import enviar_correo
from datetime import datetime
from PyPDF2 import PdfReader, PdfWriter
from docx import Document
import traceback
import hashlib
import uuid
from manejoerrores import error100
from datetime import date
from utils.extraccion import cookie100
from utils.encrypt import encrypt_information, decrypt_information


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







#usaremos esta funcion para manejar las respuetas.
def obtener_respuesta_gpt3(pregunta, key):
    conversaciones = session.get('conversaciones', [])
    contexto_conversacion = "\n".join(conversaciones)

    entrada = f"""
    (These are the user's data. Please do not display or respond with the data unless the user requests it. However,
    please answer all the questions asked.):

    - More information : The one who designed and created this bot called Genuine was the CEO of GENUINE, Adriel Capellan Diaz.
    - Chat name : Genuine
    - User's first name: {session.get('nombre')}
    - User's last name: {session.get('apellido')}
    - User's age: {session.get('anos')}
    - User's year of birth: {session.get('AAAA')}
    - User's month of birth: {session.get('MM')}
    - User's day of birth: {session.get('DD')}
    - User's email: {session.get('usuario')}
    - User's Gender: {session.get('gender')}

    Conversación:
    {contexto_conversacion}

    Usuario: {session.get('nombre')}: {pregunta}
    """

    openai.api_key = key
    respuesta = openai.Completion.create(
        engine='text-davinci-003',
        prompt=entrada,
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.4
    )

    nueva_respuesta = respuesta.choices[0].text.strip()
    nueva_respuesta = nueva_respuesta.replace("Genuine:", "")

    conversaciones.append(f"Usuario: {session.get('nombre')}: {pregunta}")
    conversaciones.append(nueva_respuesta)
    session['conversaciones'] = conversaciones
    if len(conversaciones) > 40:
        session['conversaciones'] = []
        conversaciones = []

    print(conversaciones)
    print(len(conversaciones))
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
    


#----------------------------------------------------------------Apartir de esta line usaremos las funciones de registro-------------------------------------------------------
@app.route('/auth/register', methods=["POST", "GET"])
def register():
    redirect_cookie_auth()
    try:
        redirigir_en_caso_existir_session()
        if request.method == "POST":
            id_usuario = str(uuid.uuid4())
            nombre = request.form.get('name')
            apellido = request.form.get('last_name')
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
                                       email='', contraseña='', openai='')
            except Exception as e:
                return render_template('auth/register.html', error="Error al verificar la API: " + str(e),
                                    email='', contraseña='', openai='')
            if user is None:
                cur1 = mysql.connection.cursor()
                cur1.execute("INSERT INTO verificacion VALUES (%s, %s, %s, %s)",
                             (id_usuario, reason, numeros, datetime.now()))
                cur1.close()

                cur2 = mysql.connection.cursor()
                cur2.execute("INSERT INTO usuarios VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                             (code, id_usuario, nombre, apellido, email, hash_value, api, datetime.now(), reason))
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



#--------------------------------------------------Fin de funciones de seguridad de Registro-------------------------------------------------------------------------------------
 
#--------------------------------------------Apartir de esta linea utilizaremos funciones para inicio de sesion.--------------------------------------------------------------------------

@app.route('/auth', methods=["POST", "GET"])
def login():
    redirect_cookie_auth()
    cookie100ban = request.cookies.get(cookie100)
    redirigir_en_caso_existir_session()

    if cookie100ban == "TRUE":
        send_mail_danger()
        return render_template('auth/login.html')

    if request.method == 'POST':
        return handle_login_post_request()
    else:
        return render_login_template()

def handle_login_post_request():
    try:
        usuario = request.form.get('email')
        password = request.form.get('contraseña')
        reminder = request.form.get('reminder')
        hash_value = hash_password(password)

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = %s ", (usuario,))
        user = cur.fetchone()
        cur.close()

        if user is not None:
            contraseñaalma = user[5]
            if hash_value == contraseñaalma:
                set_user_session_data(user)
                speaklocation()
                verificacion = get_user_verification_data(user)
                if verificacion is not None:
                    return handle_verification(verificacion, usuario, url = url_for('index'))
                else:
                    incrementar_intentos(usuario)
                    if failed_login_attempts[usuario] >= 4:
                        response = make_response(render_template('auth/login.html'))
                        response.set_cookie(cookie100, 'TRUE', max_age=3600*24*1)
                        return response
                    else:
                        response = make_response(render_template('auth/login.html', error='Usuario o contraseña incorrecto', usuario = '', password = ''))
                        return response
            else:
                incrementar_intentos(usuario)
                if failed_login_attempts[usuario] >= 4:
                    response = make_response(render_template('auth/login.html'))
                    response.set_cookie(cookie100, 'TRUE', max_age=1800, secure=True, httponly=True, samesite='Strict')
                    return response
                else:
                    response = make_response(render_template('auth/login.html', error='Usuario o contraseña incorrecto', usuario = '', password = ''))
                    return response
        else:
            return render_template('auth/login.html', error='Usuario o contraseña incorrecto', usuario = '', password = '')
    except Exception as e:
        traceback.print_exc()
        return render_template('auth/login.html', errorL=error100, email='', contraseña='')

def render_login_template():
    return render_template('auth/login.html')

def hash_password(password):
    hashpassword = hashlib.sha256()
    hashpassword.update(password.encode('utf8'))
    return hashpassword.hexdigest()

def set_user_session_data(user):
    session['id'] = user[0]
    session['idgenuine'] = user[1]
    session['nombre'] = user[2]
    session['apellido'] = user[3]
    session['usuario'] = user[4]
    session['api'] = user[6]
    session['datos'] = user[8]

def get_user_verification_data(user):
    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT * FROM verificacion WHERE idusuario = %s", (session['idgenuine'],))
    verificacion = cur1.fetchone()
    cur1.close()
    return verificacion

def handle_verification(verificacion, usuario, url):
    session['verificado'] = verificacion[1]
    if session['verificado'] == "NO":
        return redirect(url_for('verificacion'))
    else:
        if session['datos'] == 'NO':
            return redirect(url_for('datos'))
        else:
            if usuario in failed_login_attempts:
                del failed_login_attempts[usuario]
            manejar_datos_ip()
            return twofactor(url)

def incrementar_intentos(usuario):
    if usuario in failed_login_attempts:
        failed_login_attempts[usuario] += 1
    else:
        failed_login_attempts[usuario] = 1

    print(failed_login_attempts[usuario])

def cookie_log(iduser):
    cur5 = mysql.connection.cursor()
    cur5.execute("SELECT * FROM usuarios WHERE idusuarios = %s", (iduser, ))
    user = cur5.fetchone()
    session['id'] = user[0]
    session['idgenuine'] = user[1]
    session['nombre'] = user[2]
    session['apellido'] = user[3]
    session['usuario'] = user[4]
    session['api'] = user[6]
    session['datos'] = user[8]
    speaklocation()
    cur6 = mysql.connection.cursor()
    cur6.execute("SELECT * FROM verificacion WHERE idusuario = %s",(session['idgenuine'], ))
    verificacion = cur6.fetchone()
    if verificacion is not None:
        session['verificado'] = verificacion[1]
        print(session['verificado'])
    return redirect(url_for ('index'))

def redirect_cookie_auth():
    cookie_auth_authentication_done = request.cookies.get('data_reminder_user')
    if cookie_auth_authentication_done is not None:
            iduser = cookie_auth_authentication_done
            cookie_log(iduser)


def send_mail_danger():
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




# Diccionario para almacenar los intentos de inicio de sesión fallidos por IP
failed_login_attempts = {}




def incrementar_intentos(usuario):
    if usuario in failed_login_attempts:
        failed_login_attempts[usuario] += 1
        session['failed_login_attemptsemail'] = usuario
        print(failed_login_attempts[usuario])
    else:
        failed_login_attempts[usuario] = 1
        print(failed_login_attempts[usuario])

    # Verificar si se alcanzó el límite de intentos fallidos
    
        


def manejar_datos_ip():
                session['logued'] = True
                cur1 = mysql.connection.cursor()
                cur1.execute("SELECT * FROM datos WHERE idusuarios = %s", (session['idgenuine'],))
                datos = cur1.fetchone()
                cur1.close()
                session['anos'] = datos[1]
                session['AAAA'] = datos[2]
                session['MM'] = datos[3]
                session['DD'] = datos[4]
                session['gender'] = datos[5]
                cur3 = mysql.connection.cursor()
                cur3.execute("SELECT * FROM preferencias WHERE idusuarios = %s",
                             (session['idgenuine'],))
                preferencias = cur3.fetchone()
                if preferencias is None:
                    cur4 = mysql.connection.cursor()
                    cur4.execute("INSERT INTO preferencias VALUES (%s, %s, %s)",
                                 (session['idgenuine'], "TRUE", "FALSE"))


@app.route('/2factor', methods=['POST', 'GET'])
def twofactorpage():
    try:
        notrequired = request.cookies.get('2factor')
        if notrequired == session.get('idgenuine'):
            response = make_response(redirect(url_for('index')))
        else:
            idusuario = session.get('idgenuine')
            if request.method == 'POST':
                code1 = str(request.form.get('code1'))
                code2 = str(request.form.get('code2'))
                code3 = str(request.form.get('code3'))
                code4 = str(request.form.get('code4'))
                result = code1 + code2 + code3 + code4
                reminder = request.form.get('reminderdevice')

                verification_code = mysql.connection.cursor()
                verification_code.execute("SELECT codigo FROM verificacion WHERE idusuario = %s", (idusuario,))
                row = verification_code.fetchone()

                if row is not None:
                    verification = row[0]
                    verification_code.close()

                    if verification == result:
                        if reminder:
                            response = make_response(redirect(url_for('index')))
                            response.set_cookie('2factor', idusuario, max_age=3600*24*30)
                            response.set_cookie('data_reminder_user', idusuario, max_age=3600*24*30)
                        else:
                            response = make_response(redirect(url_for('index')))
                    else:
                        return render_template('2factor.html', error='Código incorrecto',
                                               codigo='', codigo1='', codigo2='', codigo3='', codigo4='')
                else:
                    verification_code.close()
                    return render_template('2factor.html')
            else:
                response = make_response(render_template('2factor.html'))

        return response

    except Exception as e:
        print("Error en twofactorpage:", str(e))
        return render_template('2factor.html', message='Se produjo un error')






# Aquí se manejarán funciones de autenticación.
def twofactor(url):
    notrequired = request.cookies.get('2factor')
    try:        
        if notrequired == session['idgenuine']:
                return redirect(url_for('index'))
        else:
            if notrequired is None:
                    if 'already_sent' not in session or session['already_sent']:
                        enviar_correo_2factor()
                    else:
                        print("Ya se envió un correo.")
                    return redirect(url_for('twofactorpage'))
            else:
                enviar_correo_2factor()
                return redirect(url_for('twofactorpage'))
    except Exception as e:
        print("Error en la consulta SQL:", str(e))
        return redirect(url)




         
def enviar_correo_2factor():
    try:
        idusuario = session['idgenuine']
        numeros = ''.join(random.choices(string.digits, k=4))

        # Establecer la conexión a la base de datos
        connection = mysql.connection

        # Actualizar el código de verificación en la base de datos
        with connection.cursor() as cursor:
            cursor.execute("UPDATE verificacion SET codigo = %s WHERE idusuario = %s", (numeros, idusuario))
            connection.commit()

        asunto = "Código de doble factor"
        contenido = f"""{numeros}, este es tu código de verificación de Genuine.
                        Por favor, introduce el código para iniciar sesión. Si no has solicitado un código, 
                        te recomendamos cambiar tu contraseña lo antes posible."""
        destinario = session['usuario']
        session['alreay_sent'] = True
        return enviar_correo(destinario, asunto, contenido)
    except Exception as e:
        # Manejo de excepciones
        print("Error en enviar_correo_2factor:", str(e))
        return None
        

#funcion para redirigir en caso de existir sesion.
def redirigir_en_caso_existir_session():
     if 'logued' in session and session['logued']:
        return redirect(url_for('index'))


#--------------------------------------------------Fin de funciones de seguridad de inicio de session-------------------------------------------------------------------------------------



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

            emailfilter = session['usuario']
            emailfiltrado, dominioemail = emailfilter.split("@")
            emailoculto = emailfiltrado[:3] + '*' * (len(emailfiltrado)-3)
            emailmostrar = emailoculto + '@' + dominioemail
            session['emailoculto'] = emailmostrar
            return render_template('auth/verificacion.html')

        return redirect(url_for('datos'))

    except Exception as e:
        return render_template('auth/verificacion.html', error=str(e))







@app.route('/auth/verificacion/resend')
def resend():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM verificacion WHERE idusuario = %s", (session.get('idgenuine'),))
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
    response = session.clear()
    response = make_response(redirect(url_for('home')))
    response.set_cookie('data_reminder_user', '', expires=0)
    return response


# Ruta principal, chat
@app.route('/')
def index():
    nombre = session['nombre']
    url = url_for('index')
    twofactor(url)
    session.pop('correo_2factor', None) 
    principal_mensaje = f"Hola {nombre}, estoy aquí para ayudarte. que deseas hoy?"
    return render_template('chat.html', bienvenida = principal_mensaje)


@app.route('/home')
def home():
    response = redirect_cookie_auth()
    response = redirigir_en_caso_existir_session()
    response = make_response(render_template('index.html', date = datetime.now().year))
    return response

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











def speaklocation():
    idusuario = session['idgenuine']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM preferencias WHERE idusuarios = %s", (idusuario, ))
    speak = cur.fetchone()
    cur.close()
    if speak is not None:
        speak1 = speak[1]
        session['speak'] = speak1

         

# Convertir texto a voz utilizando pyttsx3
def convertir_texto_a_voz(response):
    engine = pyttsx3.init()
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
