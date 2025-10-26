from fastapi import FastAPI, Request
from twilio.twiml.voice_response import VoiceResponse
import uvicorn
from classifier import classify_emergency_call
from pydantic import BaseModel

app = FastAPI()

# Modelo para o endpoint de classificação
class ClassifyRequest(BaseModel):
    text: str

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
