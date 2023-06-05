import mysql.connector
from flask import session




def correos():

    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ia"
    )

    cur = conexion.cursor()
    cur.execute("SELECT usuario FROM usuarios")
    emails = cur.fetchall()
    cur.close()

    print(emails)
