from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse
import uvicorn
from classifier import classify_emergency_call
from urgency_classifier import classify_police_urgency, generate_police_instructions
from firefighter_urgency_classifier import classify_firefighter_urgency, generate_firefighter_instructions
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
    
    # Se for uma emergência policial, classifica a urgência POLICIAL
    if classification['category'] in ['policia']:
        urgency_data = classify_police_urgency(transcript)
        print("🚨 Análise de Urgência POLICIAL:")
        print(f"   Nível: {urgency_data['urgency_level']}")
        print(f"   Confiança: {urgency_data['confidence']}%")
        print(f"   Motivo: {urgency_data['reasoning']}")
        
        # Gera instruções específicas para a polícia
        police_instructions = generate_police_instructions(urgency_data)
        print("📋 Instruções para Despacho POLICIAL:")
        print(police_instructions)
    
    # Se for uma emergência de bombeiros, classifica a urgência de BOMBEIROS
    elif classification['category'] in ['bombeiros']:
        urgency_data = classify_firefighter_urgency(transcript)
        print("🚒 Análise de Urgência de BOMBEIROS:")
        print(f"   Nível: {urgency_data['urgency_level']}")
        print(f"   Confiança: {urgency_data['confidence']}%")
        print(f"   Motivo: {urgency_data['reasoning']}")
        
        # Gera instruções específicas para os bombeiros
        firefighter_instructions = generate_firefighter_instructions(urgency_data)
        print("📋 Instruções para Despacho de BOMBEIROS:")
        print(firefighter_instructions)

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

@app.post("/classify-police-urgency")
async def classify_police_urgency_endpoint(request: ClassifyRequest):
    """
    Endpoint para testar classificação de urgência POLICIAL de textos mockados.
    Recebe um texto e retorna a análise de urgência policial com instruções.
    """
    urgency_data = classify_police_urgency(request.text)
    police_instructions = generate_police_instructions(urgency_data)
    
    return {
        "police_urgency_analysis": urgency_data,
        "police_instructions": police_instructions
    }

@app.post("/classify-firefighter-urgency")
async def classify_firefighter_urgency_endpoint(request: ClassifyRequest):
    """
    Endpoint para testar classificação de urgência de BOMBEIROS de textos mockados.
    Recebe um texto e retorna a análise de urgência de bombeiros com instruções.
    """
    urgency_data = classify_firefighter_urgency(request.text)
    firefighter_instructions = generate_firefighter_instructions(urgency_data)
    
    return {
        "firefighter_urgency_analysis": urgency_data,
        "firefighter_instructions": firefighter_instructions
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
