from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse
import uvicorn
from classifier import classify_emergency_call
from pydantic import BaseModel

app = FastAPI()

# Modelo para o endpoint de classificação
class ClassifyRequest(BaseModel):
    text: str

@app.get("/")
@app.post("/")
async def atender_e_falar():
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
    return Response(content=str(response), media_type='application/xml')

@app.post("/voice")
async def voice(request: Request):
    # Aqui é o que acontece quando alguém liga pro teu número
    data = await request.form()
    response = VoiceResponse()
    response.say("Olá! Você ligou para o Centro de Emergência Unificado. "
                 "Descreva sua emergência após o bip.")
    response.record(maxLength=10, action="/handle_recording", transcribe=True)
    return str(response)

@app.post("/handle_recording")
async def handle_recording(request: Request):
    data = await request.form()
    recording_url = data.get("RecordingUrl")
    transcript = data.get("TranscriptionText", "(sem transcrição)")
    print("🔊 Gravação:", recording_url)
    print("📝 Transcrição:", transcript)
    
    # Classifica automaticamente a chamada
    classification = classify_emergency_call(transcript)
    print("🎯 Classificação:")
    print(f"   Categoria: {classification['category']}")
    print(f"   Confiança: {classification['confidence']}%")
    print(f"   Motivo: {classification['reasoning']}")

    response = VoiceResponse()
    response.say("Obrigado. Sua emergência foi registrada e será atendida em breve.")
    return str(response)

@app.post("/classify")
async def classify(request: ClassifyRequest):
    """
    Endpoint para testar classificação de textos mockados.
    Recebe um texto e retorna a classificação.
    """
    classification = classify_emergency_call(request.text)
    return classification

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
