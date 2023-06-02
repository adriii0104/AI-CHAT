import requests

# Función para obtener información de Wikipedia
def obtener_informacion_wikipedia(palabra_clave):
    url = f"https://es.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&titles={palabra_clave}&format=json"
    response = requests.get(url).json()

    if 'query' in response and 'pages' in response['query']:
        pages = response['query']['pages']
        for page in pages.values():
            if 'extract' in page:
                return page['extract']

    return None



error = "El email ya está registrado"