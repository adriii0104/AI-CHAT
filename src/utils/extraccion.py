import requests

def obtener_ip_publica():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        if response.status_code == 200:
            data = response.json()
            ip_publica = data['ip']
            return ip_publica
        else:
            print('No se pudo obtener la IP pública:', response.status_code)
    except requests.RequestException as e:
        print('Error en la solicitud:', str(e))