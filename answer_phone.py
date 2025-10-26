import os
from flask import Flask, Response, request
from twilio.twiml.voice_response import VoiceResponse, Gather, Dial, Say
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict
import json

from classifiers.classifier import classify_emergency_call
from classifiers.firefighter_urgency_classifier import generate_firefighter_instructions
from classifiers.police_urgency_classifier import generate_police_instructions
from classifiers.samu_urgency_classifier import classify_samu_urgency

# --- Bloco do Classificador (Seu código) ---

# Carrega variáveis de ambiente
load_dotenv()

# Inicializa cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHECKLIST_SAMU = [
    {"id": "P1_sintoma_principal", "pergunta": "Qual é o principal sintoma agora? Por exemplo, inconsciente, dor no peito, ou sangramento."},
    {"id": "P2_consciencia_respiracao", "pergunta": "A pessoa está consciente e respirando?"},
    {"id": "P3_idade_condicoes", "pergunta": "Qual a idade aproximada e a pessoa é criança, idosa, ou gestante?"},
    {"id": "P4_sangramento_fratura", "pergunta": "Há sangramento importante ou fratura aparente?"},
    {"id": "P5_trauma_alto_risco", "pergunta": "Houve um acidente de trânsito em alta velocidade ou queda de altura?"},
    {"id": "P6_acesso_referencia", "pergunta": "Qual o endereço completo com ponto de referência e informações de acesso, como portaria ou bloco?"}
]


# --- Bloco do Servidor Flask (Atualizado) ---

app = Flask(__name__)

# Rota principal (que você vai configurar no Twilio)
@app.route("/", methods=['GET', 'POST'])
def atender_e_escutar():
    """
    PASSO 1: Atende, dá a mensagem de "fale" e começa a escutar/transcrever.
    """
    response = VoiceResponse()

    # 1. Diga a mensagem
    response.say(
        "Serviço de emergência, fale sua emergência agora.", 
        language="pt-BR", 
        voice="alice"
    )

    # 2. Instrua o Twilio a escutar e transcrever
    #    (O "action" é crucial! Ele envia o resultado para /receber_transcricao)
    response.gather(
        input="speech",
        language="pt-BR",
        speech_timeout="auto",  # Detecta o fim da fala
        action="/receber_transcricao", # Envia o texto transcrito para esta rota
        method="POST"
    )

    # 3. Fallback (se o usuário não falar nada)
    response.say("Não ouvimos você. Tente novamente.", language="pt-BR")
    response.hangup()

    return Response(str(response), content_type='application/xml')


# Rota que recebe o resultado da transcrição
@app.route("/receber_transcricao", methods=['POST'])
def receber_classificar_e_agir():
    """
    PASSO 2: Recebe a transcrição, chama a IA e decide o que fazer.
    """
    
    texto_transcrito = request.form.get('SpeechResult')
    id_chamada = request.form.get('CallSid')
    response = VoiceResponse()

    print(f"--- Chamada {id_chamada} ---")
    
    if not texto_transcrito:
        print("Erro: Transcrição falhou ou veio vazia.")
        response.say("Não foi possível entender sua solicitação. Ligue novamente.", language="pt-BR")
        response.hangup()
        return Response(str(response), content_type='application/xml')

    print(f"Texto Transcrito: {texto_transcrito}")

    # --- A MÁGICA ACONTECE AQUI ---
    # 1. Envia o texto para seu classificador OpenAI
    classificacao = classify_emergency_call(texto_transcrito)
    
    categoria = classificacao.get("category", "indefinido")
    print(f"Categoria da IA: {categoria}")
    print(f"Motivo: {classificacao.get('reasoning')}")

    # 2. Decide a ação com base na categoria da IA
    if categoria == "samu":
        # Aqui entra o checklist do SAMU por exemplo
        pergunta_p1 = CHECKLIST_SAMU[0]["pergunta"]
        response.say(f"Entendido. Vamos iniciar o checklist SAMU. {pergunta_p1}", language="pt-BR", voice="alice")
        
        # Pergunta e ouve a resposta, apontando para a nova rota
        response.gather(
            input="speech",
            language="pt-BR",
            action="/processar_checklist_samu?passo=1" # Aponta para a nova rota
        )
        # Fallback se o usuário não responder à P1
        response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()
        # retornoDoChecklist = classify_samu_urgency(texto_transcrito)
        
    
    elif categoria == "policia":
        response.say("Entendido, ocorrência policial. Transferindo para a Polícia.", language="pt-BR", voice="alice")
        response.dial("190") # Transfere para a Polícia
    
    elif categoria == "bombeiros":
        response.say("Entendido, incêndio ou resgate. Transferindo para os Bombeiros.", language="pt-BR", voice="alice")
        response.dial("193") # Transfere para os Bombeiros
    
    else: # Categoria "indefinido" ou erro
        response.say("Não foi possível classificar sua emergência. Transferindo para um atendente.", language="pt-BR", voice="alice")
        # No hackathon, transfira para um número de "fallback", ex: seu celular
        # Vou usar um número fictício para o exemplo:
        response.dial("100") # (Substitua por um número de triagem manual)

    return Response(str(response), content_type='application/xml')


# --- NOVA ROTA (Para a Resposta da P1) ---
@app.route("/processar_checklist_samu", methods=['POST'])
def processar_checklist_samu():
    """
    PASSO 3 (e 4, 5...): O "Motor" do Checklist.
    """
    passo_atual = int(request.args.get("passo", 0))
    resposta_usuario = request.form.get('SpeenchResult')
    id_chamada = request.form.get('CallSid')

    response = VoiceResponse()

    # BABY STEP
    if passo_atual == 1:
        print(f"--- [{id_chamada} Checklist SAMU ---]")
        print(f"Resposta P1 (Sintoma): {resposta_usuario}")

        # Agora, vamos fazer a P2
        pergunta_p2 = CHECKLIST_SAMU[1]["pergunta"]
        response.say(pergunta_p2, language="pt-BR", voice="alice")

        response.gather(
            input="speech",
            language="pt-BR",
            action=f"/processar_checklist_samu?passo=2"
        )

        response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()

    elif passo_atual == 2:
        print(f"--- [{id_chamada} Checklist SAMU ---]")
        print(f"Resposta P1 (Sintoma): {resposta_usuario}")
        pergunta_p3 = CHECKLIST_SAMU[2]["pergunta"]
        response.say(pergunta_p3, language="pt-BR", voice="alice")
        response.gather(
            input="speech",
            language="pt-BR",
            action=f"/processar_checklist_samu?passo=3"
        )
    elif passo_atual == 3:
        print(f"--- [{id_chamada} Checklist SAMU ---]")
        print(f"Resposta P1 (Sintoma): {resposta_usuario}")
        pergunta_p4 = CHECKLIST_SAMU[3]["pergunta"]
        response.say(pergunta_p4, language="pt-BR", voice="alice")
        response.gather(
            input="speech",
            language="pt-BR",
            action=f"/processar_checklist_samu?passo=4"
        )
    elif passo_atual == 4:
        print(f"--- [{id_chamada} Checklist SAMU ---]")
        print(f"Resposta P1 (Sintoma): {resposta_usuario}")
        pergunta_p5 = CHECKLIST_SAMU[4]["pergunta"]
        response.say(pergunta_p5, language="pt-BR", voice="alice")
        response.gather(
            input="speech",
            language="pt-BR",
            action=f"/processar_checklist_samu?passo=5"
        )
    elif passo_atual == 5:
        print(f"--- [{id_chamada} Checklist SAMU ---]")
        print(f"Resposta P1 (Sintoma): {resposta_usuario}")
        pergunta_p6 = CHECKLIST_SAMU[5]["pergunta"]
        response.say(pergunta_p6, language="pt-BR", voice="alice")
        response.gather(
            input="speech",
            language="pt-BR",
            action=f"/processar_checklist_samu?passo=6"
        )
    elif passo_atual == 6:
        print(f"--- [{id_chamada} Checklist SAMU ---]")
        print(f"--- [{id_chamada}] Checklist SAMU ---")
        print(f"Resposta P6 (Acesso): {resposta_usuario}")
        print(f"--- [{id_chamada}] Checklist Concluído ---")

        response.say("Checklist concluído. As equipes estão sendo acionadas. Encerrando chamada.", language="pt-BR", voice="alice")
        response.hangup()
    else:
        # Segurança: se algo der errado
        response.say("Ocorreu um erro no checklist. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()
    return Response(str(response), content_type='application/xml')


# Inicia o servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)