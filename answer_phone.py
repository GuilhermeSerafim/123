import os
from flask import Flask, Response
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

# Rota principal (que você vai configurar no Twilio)
@app.route("/", methods=['GET', 'POST'])
def atender_e_falar():
    """
    Como estamos no DEMO, ele vai passar uma mensagem default, mas é só apertar qualquer tecla que já inicia a nossa aplicação!
    Atende a chamada e apenas diz a mensagem.
    A chamada será desligada automaticamente depois.
    """
    
    # 1. Cria a resposta
    response = VoiceResponse()

    # 2. Diga a mensagem
    response.say(
        "Serviço de emergência, o que você precisa?", 
        language="pt-BR", 
        voice="alice"
    )

    # 3. Retorna o TwiML
    # (Como não há mais comandos, o Twilio desliga a chamada após falar)
    return Response(str(response), content_type='application/xml')


# Inicia o servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)