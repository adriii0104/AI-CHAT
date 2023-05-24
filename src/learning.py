import openai

# Configurar la clave de la API de OpenAI
openai.api_key = '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'

# Obtener respuesta utilizando la API de OpenAI
def obtener_respuesta_gpt3(pregunta):
    respuesta = openai.Completion.create(
        engine='text-davinci-003',
        prompt=pregunta,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7
    )
    return respuesta.choices[0].text.strip()

# Obtener respuesta del chatbot
def get_response(user_message):
    with open('knowledge.txt', 'a') as file:
        file.write(user_message + '\n')
    
    response = obtener_respuesta_gpt3(user_message)
    
    return response
