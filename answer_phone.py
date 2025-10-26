import os
from flask import Flask, Response, request
from twilio.twiml.voice_response import VoiceResponse, Gather, Dial, Say
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict
import json

from classifiers.classifier import classify_emergency_call
from classifiers.firefighter_urgency_classifier import generate_firefighter_instructions, classify_firefighter_urgency
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

CHECKLIST_BOMBEIROS = [
    {"id": "P1_tipo_emergencia", "pergunta": "O que está pegando fogo ou qual a emergência? Por exemplo, casa, veículo, poste ou vazamento de gás."},
    {"id": "P2_pessoas_presas", "pergunta": "Há pessoas presas ou dentro do local?"},
    {"id": "P3_visibilidade_fogo", "pergunta": "Você vê chamas altas, muita fumaça ou apenas cheiro de queimado?"},
    {"id": "P4_materiais_perigosos", "pergunta": "Há materiais perigosos no local? Como botijão de gás, produtos químicos ou energia elétrica ligada."},
    {"id": "P5_acesso_local", "pergunta": "Qual o endereço completo e como é o acesso? Por exemplo, rua estreita ou portão trancado."},
    {"id": "P6_tentativa_combate", "pergunta": "Alguém já tentou apagar? Com extintor, mangueira ou não tentou."}
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
        # Aqui entra o checklist de Bombeiros
        pergunta_p1 = CHECKLIST_BOMBEIROS[0]["pergunta"]
        response.say(f"Entendido. Vamos iniciar o checklist dos Bombeiros. {pergunta_p1}", language="pt-BR", voice="alice")
        
        # Pergunta e ouve a resposta, apontando para a nova rota
        response.gather(
            input="speech",
            language="pt-BR",
            action="/processar_checklist_bombeiros?passo=1"
        )
        # Fallback se o usuário não responder à P1
        response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()
    
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
    PASSO 3 (e 4, 5, 6): O "Motor" do Checklist.
    """
    passo_atual = int(request.args.get("passo", 0))
    resposta_usuario = request.form.get('SpeechResult')  # Corrigido o typo
    id_chamada = request.form.get('CallSid')

    response = VoiceResponse()

    # BABY STEP
    if passo_atual == 1:
        print(f"--- [{id_chamada}] Checklist SAMU ---")
        print(f"Resposta P1 (Sintoma): {resposta_usuario}")

        # Armazena a resposta P1 e vai para P2
        r1 = resposta_usuario or ""
        pergunta_p2 = CHECKLIST_SAMU[1]["pergunta"]
        response.say(pergunta_p2, language="pt-BR", voice="alice")

        response.gather(
            input="speech",
            language="pt-BR",
            action=f"/processar_checklist_samu?passo=2&r1={r1}"
        )

        response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()

    elif passo_atual == 2:
        print(f"--- [{id_chamada}] Checklist SAMU ---")
        print(f"Resposta P2 (Consciência): {resposta_usuario}")
        
        # Recupera resposta anterior e armazena P2
        r1 = request.args.get("r1", "")
        r2 = resposta_usuario or ""
        pergunta_p3 = CHECKLIST_SAMU[2]["pergunta"]
        response.say(pergunta_p3, language="pt-BR", voice="alice")
        
        response.gather(
            input="speech",
            language="pt-BR",
            action=f"/processar_checklist_samu?passo=3&r1={r1}&r2={r2}"
        )
        
        response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()
        
    elif passo_atual == 3:
        print(f"--- [{id_chamada}] Checklist SAMU ---")
        print(f"Resposta P3 (Idade/Condições): {resposta_usuario}")
        
        # Recupera respostas anteriores e armazena P3
        r1 = request.args.get("r1", "")
        r2 = request.args.get("r2", "")
        r3 = resposta_usuario or ""
        pergunta_p4 = CHECKLIST_SAMU[3]["pergunta"]
        response.say(pergunta_p4, language="pt-BR", voice="alice")
        
        response.gather(
            input="speech",
            language="pt-BR",
            action=f"/processar_checklist_samu?passo=4&r1={r1}&r2={r2}&r3={r3}"
        )
        
        response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()
        
    elif passo_atual == 4:
        print(f"--- [{id_chamada}] Checklist SAMU ---")
        print(f"Resposta P4 (Sangramento/Fratura): {resposta_usuario}")
        
        # Recupera respostas anteriores e armazena P4
        r1 = request.args.get("r1", "")
        r2 = request.args.get("r2", "")
        r3 = request.args.get("r3", "")
        r4 = resposta_usuario or ""
        pergunta_p5 = CHECKLIST_SAMU[4]["pergunta"]
        response.say(pergunta_p5, language="pt-BR", voice="alice")
        
        response.gather(
            input="speech",
            language="pt-BR",
            action=f"/processar_checklist_samu?passo=5&r1={r1}&r2={r2}&r3={r3}&r4={r4}"
        )
        
        response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()
        
    elif passo_atual == 5:
        print(f"--- [{id_chamada}] Checklist SAMU ---")
        print(f"Resposta P5 (Trauma): {resposta_usuario}")
        
        # Recupera respostas anteriores e armazena P5
        r1 = request.args.get("r1", "")
        r2 = request.args.get("r2", "")
        r3 = request.args.get("r3", "")
        r4 = request.args.get("r4", "")
        r5 = resposta_usuario or ""
        pergunta_p6 = CHECKLIST_SAMU[5]["pergunta"]
        response.say(pergunta_p6, language="pt-BR", voice="alice")
        
        response.gather(
            input="speech",
            language="pt-BR",
            action=f"/processar_checklist_samu?passo=6&r1={r1}&r2={r2}&r3={r3}&r4={r4}&r5={r5}"
        )
        
        response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()
        
    elif passo_atual == 6:
        print(f"--- [{id_chamada}] Checklist SAMU - FINAL ---")
        print(f"Resposta P6 (Endereço): {resposta_usuario}")
        
        # Recupera TODAS as respostas anteriores e armazena P6
        r1 = request.args.get("r1", "")
        r2 = request.args.get("r2", "")
        r3 = request.args.get("r3", "")
        r4 = request.args.get("r4", "")
        r5 = request.args.get("r5", "")
        r6 = resposta_usuario or ""
        
        # Monta o texto completo com todas as respostas para o classificador
        texto_completo = f"""
P1 - Sintoma principal: {r1}
P2 - Consciência e respiração: {r2}
P3 - Idade e condições: {r3}
P4 - Sangramento ou fratura: {r4}
P5 - Trauma de alto risco: {r5}
P6 - Endereço e acesso: {r6}
"""
        
        print(f"\n=== ENVIANDO PARA CLASSIFICADOR SAMU ===")
        print(texto_completo)
        
        # Chama o classificador do SAMU
        resultado = classify_samu_urgency(texto_completo)
        
        nivel_urgencia = resultado.get("urgency_level", "MÉDIA")
        razao = resultado.get("reasoning", "Não informado")
        
        print(f"✓ Nível de Urgência: {nivel_urgencia}")
        print(f"✓ Razão: {razao}")
        
        # Responde ao usuário com o nível de urgência
        mensagem_final = f"Checklist concluído. Sua emergência foi classificada como {nivel_urgencia}. Aguarde a chegada da ambulância."
        response.say(mensagem_final, language="pt-BR", voice="alice")
        response.hangup()
        
    else:
        # Segurança: se algo der errado
        response.say("Ocorreu um erro no checklist. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()
        
    return Response(str(response), content_type='application/xml')


# --- ROTA PARA CHECKLIST DE BOMBEIROS ---
@app.route("/processar_checklist_bombeiros", methods=['POST'])
def processar_checklist_bombeiros():
    """
    Motor do Checklist dos Bombeiros.
    """
    passo_atual = int(request.args.get("passo", 0))
    resposta_usuario = request.form.get('SpeechResult')
    id_chamada = request.form.get('CallSid')

    response = VoiceResponse()

    if passo_atual == 1:
        print(f"--- [{id_chamada}] Checklist Bombeiros ---")
        print(f"Resposta P1 (Tipo): {resposta_usuario}")

        r1 = resposta_usuario or ""
        pergunta_p2 = CHECKLIST_BOMBEIROS[1]["pergunta"]
        response.say(pergunta_p2, language="pt-BR", voice="alice")

        response.gather(
            input="speech",
            language="pt-BR",
            action=f"/processar_checklist_bombeiros?passo=2&r1={r1}"
        )

        response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()

    elif passo_atual == 2:
        print(f"--- [{id_chamada}] Checklist Bombeiros ---")
        print(f"Resposta P2 (Pessoas Presas): {resposta_usuario}")
        
        r1 = request.args.get("r1", "")
        r2 = resposta_usuario or ""
        pergunta_p3 = CHECKLIST_BOMBEIROS[2]["pergunta"]
        response.say(pergunta_p3, language="pt-BR", voice="alice")
        
        response.gather(
            input="speech",
            language="pt-BR",
            action=f"/processar_checklist_bombeiros?passo=3&r1={r1}&r2={r2}"
        )
        
        response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()
        
    elif passo_atual == 3:
        print(f"--- [{id_chamada}] Checklist Bombeiros ---")
        print(f"Resposta P3 (Visibilidade): {resposta_usuario}")
        
        r1 = request.args.get("r1", "")
        r2 = request.args.get("r2", "")
        r3 = resposta_usuario or ""
        pergunta_p4 = CHECKLIST_BOMBEIROS[3]["pergunta"]
        response.say(pergunta_p4, language="pt-BR", voice="alice")
        
        response.gather(
            input="speech",
            language="pt-BR",
            action=f"/processar_checklist_bombeiros?passo=4&r1={r1}&r2={r2}&r3={r3}"
        )
        
        response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()
        
    elif passo_atual == 4:
        print(f"--- [{id_chamada}] Checklist Bombeiros ---")
        print(f"Resposta P4 (Materiais): {resposta_usuario}")
        
        r1 = request.args.get("r1", "")
        r2 = request.args.get("r2", "")
        r3 = request.args.get("r3", "")
        r4 = resposta_usuario or ""
        pergunta_p5 = CHECKLIST_BOMBEIROS[4]["pergunta"]
        response.say(pergunta_p5, language="pt-BR", voice="alice")
        
        response.gather(
            input="speech",
            language="pt-BR",
            action=f"/processar_checklist_bombeiros?passo=5&r1={r1}&r2={r2}&r3={r3}&r4={r4}"
        )
        
        response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()
        
    elif passo_atual == 5:
        print(f"--- [{id_chamada}] Checklist Bombeiros ---")
        print(f"Resposta P5 (Acesso): {resposta_usuario}")
        
        r1 = request.args.get("r1", "")
        r2 = request.args.get("r2", "")
        r3 = request.args.get("r3", "")
        r4 = request.args.get("r4", "")
        r5 = resposta_usuario or ""
        pergunta_p6 = CHECKLIST_BOMBEIROS[5]["pergunta"]
        response.say(pergunta_p6, language="pt-BR", voice="alice")
        
        response.gather(
            input="speech",
            language="pt-BR",
            action=f"/processar_checklist_bombeiros?passo=6&r1={r1}&r2={r2}&r3={r3}&r4={r4}&r5={r5}"
        )
        
        response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()
        
    elif passo_atual == 6:
        print(f"--- [{id_chamada}] Checklist Bombeiros - FINAL ---")
        print(f"Resposta P6 (Combate): {resposta_usuario}")
        
        r1 = request.args.get("r1", "")
        r2 = request.args.get("r2", "")
        r3 = request.args.get("r3", "")
        r4 = request.args.get("r4", "")
        r5 = request.args.get("r5", "")
        r6 = resposta_usuario or ""
        
        # Monta o texto completo com todas as respostas para o classificador
        texto_completo = f"""
P1 - Tipo de emergência: {r1}
P2 - Pessoas presas: {r2}
P3 - Visibilidade do fogo: {r3}
P4 - Materiais perigosos: {r4}
P5 - Acesso ao local: {r5}
P6 - Tentativa de combate: {r6}
"""
        
        print(f"\n=== ENVIANDO PARA CLASSIFICADOR BOMBEIROS ===")
        print(texto_completo)
        
        # Chama o classificador de Bombeiros
        resultado = classify_firefighter_urgency(texto_completo)
        
        nivel_urgencia = resultado.get("urgency_level", "MÉDIA")
        razao = resultado.get("reasoning", "Não informado")
        
        print(f"✓ Nível de Urgência: {nivel_urgencia}")
        print(f"✓ Razão: {razao}")
        
        # Responde ao usuário com o nível de urgência
        mensagem_final = f"Checklist concluído. Sua emergência foi classificada como {nivel_urgencia}. Aguarde a chegada dos bombeiros."
        response.say(mensagem_final, language="pt-BR", voice="alice")
        response.hangup()
        
    else:
        response.say("Ocorreu um erro no checklist. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()
        
    return Response(str(response), content_type='application/xml')


# Inicia o servidor
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)