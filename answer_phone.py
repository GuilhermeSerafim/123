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

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHECKLIST_SAMU = [
    {"id": "P1_sintoma_principal", "pergunta": "Qual é o principal sintoma agora? Por exemplo, inconsciente, dor no peito, ou sangramento."},
    {"id": "P2_consciencia_respiracao", "pergunta": "A pessoa está consciente e respirando?"},
    {"id": "P3_idade_condicoes", "pergunta": "Qual a idade aproximada e a pessoa é criança, idosa, ou gestante?"},
    {"id": "P4_sangramento_fratura", "pergunta": "Há sangramento importante ou fratura aparente?"},
    {"id": "P5_trauma_alto_risco", "pergunta": "Houve um acidente de trânsito em alta velocidade ou queda de altura?"},
    {"id": "P6_acesso_referencia", "pergunta": "Qual o endereço completo com ponto de referência e informações de acesso, como portaria ou bloco?"}
]

CHECKLIST_POLICIA = [
    {"id": "P1_autor_presente", "pergunta": "O autor ainda está presente?"},
    {"id": "P2_armas_envolvidas", "pergunta": "Há armas envolvidas?"},
    {"id": "P3_descricao_fuga", "pergunta": "Descreva o autor e a direção de fuga, se souber."},
    {"id": "P4_flagrante", "pergunta": "O crime está ocorrendo agora ou acabou de ocorrer?"},
    {"id": "P5_vitimas_feridas", "pergunta": "Há vítimas feridas no local?"},
    {"id": "P6_local_seguro", "pergunta": "O local onde você está é seguro para falar?"}
]

CHECKLIST_BOMBEIROS = [
    {"id": "P1_tipo_emergencia", "pergunta": "O que está pegando fogo ou qual a emergência técnica? Por exemplo, residência, veículo, vazamento de gás ou queda de árvore."},
    {"id": "P2_pessoas_presas", "pergunta": "Há pessoas presas ou inconscientes?"},
    {"id": "P3_chamas_fumaca", "pergunta": "Você vê chamas, muita fumaça ou só cheiro de queimado?"},
    {"id": "P4_materiais_perigosos", "pergunta": "Há materiais perigosos no local, como botijão de gás, produtos químicos ou combustíveis?"},
    {"id": "P5_acesso", "pergunta": "Como é o acesso ao local? A rua é estreita ou tem algum portão trancado?"},
    {"id": "P6_tentativa_combate", "pergunta": "Alguém já tentou combater o fogo, por exemplo, com extintor ou mangueira?"}
]

app = Flask(__name__)

respostas = []

@app.route("/", methods=['GET', 'POST'])
def atender_e_escutar():
    """
    PASSO 1: Atende, dá a mensagem de "fale" e começa a escutar/transcrever.
    """

    respostas.clear()

    response = VoiceResponse()
    response.say(
        "Serviço de emergência, fale sua emergência agora.", 
        language="pt-BR", 
        voice="alice"
    )
    response.gather(
        input="speech",
        language="pt-BR",
        speech_timeout="auto",
        action="/receber_transcricao",
        method="POST"
    )
    response.say("Não ouvimos você. Tente novamente.", language="pt-BR")
    response.hangup()
    return Response(str(response), content_type='application/xml')

@app.route("/receber_transcricao", methods=['POST'])
def receber_classificar_e_agir():
    """
    PASSO 2: Recebe a transcrição, chama a IA e decide o que fazer.
    """
    
    texto_transcrito = request.form.get('SpeechResult')
    response = VoiceResponse()

    if not texto_transcrito:
        print("Erro: Transcrição falhou ou veio vazia.")
        response.say("Não foi possível entender sua solicitação. Ligue novamente.", language="pt-BR")
        response.hangup()
        return Response(str(response), content_type='application/xml')

    print(f"Texto Transcrito: {texto_transcrito}")
    classificacao = classify_emergency_call(texto_transcrito) # AI
    categoria = classificacao.get("category", "indefinido")
    print(f"Categoria da IA: {categoria}")
    print(f"Motivo: {classificacao.get('reasoning')}")
    respostas.append(f"P0_descricao: {texto_transcrito}")

    if categoria == "samu":
        pergunta_p1 = CHECKLIST_SAMU[0]["pergunta"]
        response.say(f"Entendido. Vamos iniciar o checklist SAMU. {pergunta_p1}", language="pt-BR", voice="alice")
        
        response.gather(
            input="speech",
            language="pt-BR",
            action="/processar_checklist_samu?passo=1"
        )
        response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()
    
    elif categoria == "policia":
        pergunta_p1 = CHECKLIST_POLICIA[0]["pergunta"]
        response.say(f"Entendido. Vamos iniciar o checklist POLICIA. {pergunta_p1}", language="pt-BR", voice="alice")
        
        response.gather(
            input="speech",
            language="pt-BR",
            action="/processar_checklist_policia?passo=1"
        )
        response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()
    
    elif categoria == "bombeiros":
        response.say("Entendido, incêndio ou resgate. Transferindo para os Bombeiros.", language="pt-BR", voice="alice")
        response.dial("193") 
    
    else:
        response.say("Não foi possível classificar sua emergência. Transferindo para policia.", language="pt-BR", voice="alice")
        response.dial("190")

    return Response(str(response), content_type='application/xml')

@app.route("/processar_checklist_samu", methods=['POST'])
def processar_checklist_samu():
    """
    PASSO 3 (e 4, 5...): O "Motor" do Checklist.
    """
    passo_atual = int(request.args.get("passo", 0))
    resposta_usuario = request.form.get('SpeechResult')
    id_chamada = request.form.get('CallSid')

    response = VoiceResponse()

    if passo_atual == 1:
        print(f"Resposta P1 (Sintoma): {resposta_usuario}")
        respostas.append(f"P1_sintoma: {resposta_usuario}")

        pergunta_p2 = CHECKLIST_SAMU[1]["pergunta"]
        response.say(pergunta_p2, language="pt-BR", voice="alice")
        response.gather(
            input="speech",
            language="pt-BR",
            action=f"/processar_checklist_samu?passo=2"
        )
    elif passo_atual == 2:
        print(f"Resposta P2 (Consciência): {resposta_usuario}")
        respostas.append(f"P2_consciencia: {resposta_usuario}")
        pergunta_p3 = CHECKLIST_SAMU[2]["pergunta"]
        response.say(pergunta_p3, language="pt-BR", voice="alice")
        response.gather(
            input="speech",
            language="pt-BR",
            action=f"/processar_checklist_samu?passo=3"
        )
    elif passo_atual == 3:
        print(f"Resposta P3 (Idade/Condições): {resposta_usuario}")
        respostas.append(f"P3_idade: {resposta_usuario}")
        pergunta_p4 = CHECKLIST_SAMU[3]["pergunta"]
        response.say(pergunta_p4, language="pt-BR", voice="alice")
        response.gather(
            input="speech",
            language="pt-BR",
            action=f"/processar_checklist_samu?passo=4"
        )
    elif passo_atual == 4:
        print(f"Resposta P4 (Sangramento/Fratura): {resposta_usuario}")
        respostas.append(f"P4_sangramento: {resposta_usuario}")
        pergunta_p5 = CHECKLIST_SAMU[4]["pergunta"]
        response.say(pergunta_p5, language="pt-BR", voice="alice")
        response.gather(
            input="speech",
            language="pt-BR",
            action=f"/processar_checklist_samu?passo=5"
        )
    elif passo_atual == 5:
        print(f"Resposta P5 (Trauma): {resposta_usuario}")
        respostas.append(f"P5_trauma: {resposta_usuario}")
        pergunta_p6 = CHECKLIST_SAMU[5]["pergunta"]
        response.say(pergunta_p6, language="pt-BR", voice="alice")
        response.gather(
            input="speech",
            language="pt-BR",
            action=f"/processar_checklist_samu?passo=6"
        )
    elif passo_atual == 6:
        print(f"Resposta P6 (Acesso): {resposta_usuario}")
        respostas.append(f"P6_acesso: {resposta_usuario}")
        
        print(f"--- [{id_chamada}] Checklist Concluído ---")

        print("DADOS FINAIS COLETADOS (do array global):")
        print(respostas)
        
        response.say("Checklist concluído. As equipes estão sendo acionadas. Encerrando chamada.", language="pt-BR", voice="alice")
        response.hangup()
    else:
        response.say("Ocorreu um erro no checklist. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()

    if "gather" in str(response):
         response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
         response.hangup()
         
    return Response(str(response), content_type='application/xml')

@app.route("/processar_checklist_policia", methods=['POST'])
def processar_checklist_policia():
    """
    PASSO 3, 4, 5...: O "Motor" do Checklist da POLÍCIA.
    """
    passo_atual = int(request.args.get("passo", 0))
    resposta_usuario = request.form.get('SpeechResult')
    id_chamada = request.form.get('CallSid')

    response = VoiceResponse()

    if passo_atual == 1:
        # Respondeu P1. Vamos perguntar P2.
        print(f"Resposta P1 (Autor presente): {resposta_usuario}")
        respostas.append(f"P1_autor: {resposta_usuario}")

        # Pergunta P2
        pergunta_p2 = CHECKLIST_POLICIA[1]["pergunta"]
        response.say(pergunta_p2, language="pt-BR", voice="alice")
        response.gather(
            input="speech", language="pt-BR",
            speech_timeout="1",
            action=f"/processar_checklist_policia?passo=2"
        )

    elif passo_atual == 2:
        # Respondeu P2. Vamos perguntar P3.
        print(f"Resposta P2 (Armas): {resposta_usuario}")
        respostas.append(f"P2_armas: {resposta_usuario}")

        # Pergunta P3
        pergunta_p3 = CHECKLIST_POLICIA[2]["pergunta"]
        response.say(pergunta_p3, language="pt-BR", voice="alice")
        response.gather(
            input="speech", language="pt-BR",
            speech_timeout="1",
            action=f"/processar_checklist_policia?passo=3"
        )
        
    elif passo_atual == 3:
        # Respondeu P3. Vamos perguntar P4.
        print(f"Resposta P3 (Descrição/Fuga): {resposta_usuario}")
        respostas.append(f"P3_descricao: {resposta_usuario}")

        # Pergunta P4
        pergunta_p4 = CHECKLIST_POLICIA[3]["pergunta"]
        response.say(pergunta_p4, language="pt-BR", voice="alice")
        response.gather(
            input="speech", language="pt-BR",
            speech_timeout="1",
            action=f"/processar_checklist_policia?passo=4"
        )
        
    elif passo_atual == 4:
        # Respondeu P4. Vamos perguntar P5.
        print(f"Resposta P4 (Flagrante): {resposta_usuario}")
        respostas.append(f"P4_flagrante: {resposta_usuario}")

        # Pergunta P5
        pergunta_p5 = CHECKLIST_POLICIA[4]["pergunta"]
        response.say(pergunta_p5, language="pt-BR", voice="alice")
        response.gather(
            input="speech", language="pt-BR",
            speech_timeout="1",
            action=f"/processar_checklist_policia?passo=5"
        )
        
    elif passo_atual == 5:
        # Respondeu P5. Vamos perguntar P6.
        print(f"Resposta P5 (Vítimas feridas): {resposta_usuario}")
        respostas.append(f"P5_vitimas: {resposta_usuario}")

        # Pergunta P6
        pergunta_p6 = CHECKLIST_POLICIA[5]["pergunta"]
        response.say(pergunta_p6, language="pt-BR", voice="alice")
        response.gather(
            input="speech", language="pt-BR",
            speech_timeout="1",
            action=f"/processar_checklist_policia?passo=6"
        )
        
    elif passo_atual == 6:
        # Respondeu P6. O CHECKLIST ACABOU.
        print(f"Resposta P6 (Local seguro): {resposta_usuario}")
        respostas.append(f"P6_local: {resposta_usuario}")

        print(f"--- [{id_chamada}] Checklist POLÍCIA Concluído ---")
        
        # PROVA DE QUE FUNCIONOU:
        print("DADOS FINAIS COLETADOS (do array global):")
        print(respostas)

        response.say("Checklist da polícia concluído. Aguarde as instruções e a chegada da viatura. Encerrando chamada.", language="pt-BR", voice="alice")
        response.hangup()
        
    else:
        # Segurança
        response.say("Ocorreu um erro no checklist. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()

    # Fallback (se o usuário não responder a P2, P3, etc.)
    if "gather" in str(response):
         response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
         response.hangup()
         
    return Response(str(response), content_type='application/xml')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)