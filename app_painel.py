"""
EXEMPLO COMPLETO: Como Integrar Painel ao seu Backend FastAPI

Este arquivo mostra a forma COMPLETA de integração do painel ao seu app.py atual
"""

from fastapi import FastAPI, Request, Depends
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.voice_response import VoiceResponse
import uvicorn
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import func

# ============================================================================
# 1. IMPORTAR SUAS FUNÇÕES DE CLASSIFICAÇÃO EXISTENTES
# ============================================================================

from classifiers import (
    classify_emergency_call,
    classify_police_urgency, 
    generate_police_instructions,
    classify_firefighter_urgency,
    generate_firefighter_instructions,
    classify_samu_urgency,
    generate_samu_instructions
)

# ============================================================================
# 2. IMPORTAR O MÓDULO DO DASHBOARD COM BANCO DE DADOS
# ============================================================================

from dashboard_db import setup_dashboard_routes, add_call_to_db
from database import get_db
from sqlalchemy.orm import Session

# ============================================================================
# 3. INICIALIZAR FASTAPI COM CORS
# ============================================================================

app = FastAPI(
    title="Unificador de Emergências",
    description="API de classificação de emergências com dashboard",
    version="1.0.0"
)

# Adicionar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Vite dev (frontend)
        "http://localhost:3000",      # React dev alternativo
        "http://localhost:8000",      # Backend dev
        "http://127.0.0.1:5173",
        # Em produção, adicione os domínios reais:
        # "https://seu-frontend.com",
        # "https://seu-backend.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# 4. SETUP DAS ROTAS DO DASHBOARD
# ============================================================================

setup_dashboard_routes(app)

# ============================================================================
# 5. SUAS ROTAS EXISTENTES (com integração ao banco de dados)
# ============================================================================

@app.get("/")
@app.post("/")
async def atender_e_falar():
    """
    Atende a chamada e diz a mensagem inicial.
    """
    response = VoiceResponse()
    response.say(
        "Serviço de emergência, o que você precisa?", 
        language="pt-BR", 
        voice="alice"
    )
    return Response(content=str(response), media_type='application/xml')

@app.post("/voice")
async def voice(request: Request):
    """Atende ligação e pede para gravar mensagem"""
    data = await request.form()
    response = VoiceResponse()
    response.say(
        "Olá! Você ligou para o Centro de Emergência Unificado. "
        "Descreva sua emergência após o bip."
    )
    response.record(maxLength=10, action="/handle_recording", transcribe=True)
    return Response(content=str(response), media_type='application/xml')

@app.post("/handle_recording")
async def handle_recording(request: Request, db: Session = Depends(get_db)):
    """
    Processa a gravação e classifica a emergência
    INTEGRAÇÃO: Salva dados no banco de dados
    """
    data = await request.form()
    recording_url = data.get("RecordingUrl")
    transcript = data.get("TranscriptionText", "(sem transcrição)")
    
    print("🔊 Gravação:", recording_url)
    print("📝 Transcrição:", transcript)
    
    # ========================================================================
    # CLASSIFICAÇÃO DE EMERGÊNCIA
    # ========================================================================
    
    classification = classify_emergency_call(transcript)
    print("🎯 Classificação:")
    print(f"   Categoria: {classification['category']}")
    print(f"   Confiança: {classification['confidence']}%")
    print(f"   Motivo: {classification['reasoning']}")
    
    # ========================================================================
    # PREPARAR DADOS PARA O BANCO
    # ========================================================================
    
    call_count = db.query(func.count(1)).scalar()
    
    call_data = {
        'id': f'call_{call_count + 1:06d}',
        'timestamp': datetime.now(),
        'transcript': transcript,
        'category': classification['category'],
        'confidence': classification['confidence'],
        'urgency_level': None,  # Será preenchido abaixo
        'reasoning': classification['reasoning'],
        'region': None  # Pode ser preenchido se você tiver detecção de região
    }
    
    # ========================================================================
    # CLASSIFICAÇÃO DE URGÊNCIA (por categoria)
    # ========================================================================
    
    if classification['category'] in ['policia']:
        urgency_data = classify_police_urgency(transcript)
        print("🚨 Análise de Urgência POLICIAL:")
        print(f"   Nível: {urgency_data['urgency_level']}")
        print(f"   Confiança: {urgency_data['confidence']}%")
        
        # Atualizar dados com urgência
        call_data['urgency_level'] = urgency_data['urgency_level']
        
        # Gerar instruções
        police_instructions = generate_police_instructions(urgency_data)
        print("📋 Instruções para Despacho POLICIAL:")
        print(police_instructions)
        
        # Aqui você poderia despachar para polícia automaticamente
        # dispatch_police(urgency_data)
    
    elif classification['category'] in ['bombeiros']:
        urgency_data = classify_firefighter_urgency(transcript)
        print("🚒 Análise de Urgência de BOMBEIROS:")
        print(f"   Nível: {urgency_data['urgency_level']}")
        print(f"   Confiança: {urgency_data['confidence']}%")
        
        call_data['urgency_level'] = urgency_data['urgency_level']
        
        firefighter_instructions = generate_firefighter_instructions(urgency_data)
        print("📋 Instruções para Despacho de BOMBEIROS:")
        print(firefighter_instructions)
    
    elif classification['category'] in ['samu']:
        urgency_data = classify_samu_urgency(transcript)
        print("🚑 Análise de Urgência do SAMU:")
        print(f"   Nível: {urgency_data['urgency_level']}")
        print(f"   Confiança: {urgency_data['confidence']}%")
        
        call_data['urgency_level'] = urgency_data['urgency_level']
        
        samu_instructions = generate_samu_instructions(urgency_data)
        print("📋 Instruções para Despacho do SAMU:")
        print(samu_instructions)
    
    # ========================================================================
    # SALVAR NO BANCO DE DADOS
    # ========================================================================
    
    saved_call = add_call_to_db(db, call_data)
    print(f"\n✅ Chamada salva no banco (ID: {saved_call.id})")
    
    # Retorna resposta TwiML
    response = VoiceResponse()
    if classification['category'] == 'trote':
        response.say("Percebemos que esta é uma ligação falsa. Não podemos atender.", language="pt-BR")
    else:
        response.say(f"Entendido. Enviando ajuda de {classification['category']}.", language="pt-BR")
    
    return Response(content=str(response), media_type='application/xml')

# ============================================================================
# 6. ENDPOINTS ADICIONAIS ÚTEIS
# ============================================================================

@app.get("/info")
async def info(db: Session = Depends(get_db)) -> JSONResponse:
    """Informações sobre a API"""
    total_calls = db.query(func.count(1)).scalar()
    return JSONResponse({
        "name": "Unificador de Emergências",
        "version": "1.0.0",
        "total_calls": total_calls,
        "api_url": "http://localhost:8000",
        "docs": "http://localhost:8000/docs"
    })

@app.get("/test-classify")
async def test_classify(text: str = "Tem um incêndio", db: Session = Depends(get_db)) -> JSONResponse:
    """Endpoint para testar classificação sem Twilio"""
    try:
        classification = classify_emergency_call(text)
        
        call_count = db.query(func.count(1)).scalar()
        call_data = {
            'id': f'call_test_{call_count + 1:06d}',
            'timestamp': datetime.now(),
            'transcript': text,
            'category': classification['category'],
            'confidence': classification['confidence'],
            'urgency_level': 'média',
            'reasoning': classification['reasoning'],
            'region': None
        }
        
        saved_call = add_call_to_db(db, call_data)
        
        return JSONResponse({
            "status": "success",
            "classification": classification,
            "saved_to_database": True,
            "call_id": saved_call.id
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# ============================================================================
# 7. INICIAR SERVIDOR
# ============================================================================

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║   🚨 UNIFICADOR DE EMERGÊNCIAS - COM DASHBOARD 📊            ║
    ╠════════════════════════════════════════════════════════════════╣
    ║                                                                ║
    ║   API:           http://localhost:8000                        ║
    ║   Docs:          http://localhost:8000/docs                   ║
    ║   Dashboard:     http://localhost:5173 (frontend)             ║
    ║                                                                ║
    ║   Endpoints principais:                                       ║
    ║   - GET  /health         Verificar status                     ║
    ║   - GET  /stats          Estatísticas do dashboard            ║
    ║   - GET  /history        Histórico de chamadas                ║
    ║   - POST /classify       Classificar uma emergência           ║
    ║   - GET  /info           Informações da API                   ║
    ║                                                                ║
    ║   Para testar:                                                ║
    ║   curl http://localhost:8000/stats                            ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

# ============================================================================
# COMO USAR ESTE ARQUIVO
# ============================================================================

"""
1. Copie este arquivo para substituir seu app.py ou mescle o conteúdo

2. Execute:
   python -m uvicorn app:app --reload --port 8000

3. Teste:
   curl http://localhost:8000/stats
   curl "http://localhost:8000/test-classify?text=Tem%20um%20incendio"

4. Acesse o dashboard:
   http://localhost:5173 (certifique-se que o frontend está rodando)

5. Integração com Twilio:
   - Configure seu número Twilio para chamar http://seu-servidor.com/voice
   - Quando alguém ligar, a chamada será processada e salva no dashboard

FLUXO COMPLETO:
  Chamada Twilio → /voice → /handle_recording 
  → classify_emergency_call() → save to dashboard 
  → frontend visualiza em tempo real via GET /stats
"""
