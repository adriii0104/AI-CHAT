import mysql.connector
from flask import session




def correos():
    id = session.get('idblid')

    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ia"
    )

    cur = conexion.cursor()
    cur.execute("SELECT * FROM verificacion WHERE idblid = (%s,)",
                (id, ))
    codigo_verificacion = cur.fetchone()
    cur.close()

    return codigo_verificacion[2]
