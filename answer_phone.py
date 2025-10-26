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
    # 1. A pessoa pode falar?
    {"id": "P1_local_seguro", "pergunta": "O local onde você está é seguro para falar?"},
    
    # 2. Onde é a emergência? (A pergunta que você queria mover)
    {"id": "P2_acesso_referencia", "pergunta": "Qual o endereço completo com ponto de referência e informações de acesso, como portaria ou bloco?"},
    
    # 3. Qual é a urgência?
    {"id": "P3_flagrante", "pergunta": "O crime está ocorrendo agora ou acabou de ocorrer?"},
    
    # 4. Há vítimas? (Decide se o SAMU também vai)
    {"id": "P5_vitimas_feridas", "pergunta": "Há vítimas feridas no local?"},
    
    # 5. Qual o risco imediato?
    {"id": "P1_autor_presente", "pergunta": "O autor ainda está presente?"},
    
    # 6. Qual o nível do risco?
    {"id": "P2_armas_envolvidas", "pergunta": "Há armas envolvidas?"},
    
    # 7. Detalhes para a viatura
    {"id": "P3_descricao_fuga", "pergunta": "Descreva o autor e a direção de fuga, se souber."}
]

CHECKLIST_BOMBEIROS = [
    # 1. Onde é a emergência?
    {"id": "P7_acesso_referencia", "pergunta": "Qual o endereço completo com ponto de referência e informações de acesso, como portaria ou bloco?"},

    # 2. Qual é a emergência?
    {"id": "P1_tipo_emergencia", "pergunta": "O que está pegando fogo ou qual a emergência técnica? Por exemplo, residência, veículo, vazamento de gás ou queda de árvore."},

    # 3. Risco imediato à vida?
    {"id": "P2_pessoas_presas", "pergunta": "Há pessoas presas ou inconscientes?"},

    # 4. Gravidade
    {"id": "P3_chamas_fumaca", "pergunta": "Você vê chamas, muita fumaça ou só cheiro de queimado?"},

    # 5. Riscos adicionais
    {"id": "P4_materiais_perigosos", "pergunta": "Há materiais perigosos no local, como botijão de gás, produtos químicos ou combustíveis?"},
    
    # 6. Detalhes de acesso
    {"id": "P5_acesso", "pergunta": "Como é o acesso ao local? A rua é estreita ou tem algum portão trancado?"},

    # 7. Ações no local
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
        pergunta_p1 = CHECKLIST_POLICIA[0]["pergunta"]
        response.say(f"Entendido. Vamos iniciar o checklist BOMBEIRO. {pergunta_p1}", language="pt-BR", voice="alice")
        
        response.gather(
            input="speech",
            language="pt-BR",
            action="/processar_checklist_bombeiros?passo=1"
        )
        response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()
    
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

    # Pega o ID da pergunta ANTERIOR (a que foi respondida)
    # Ex: se passo_atual=1, respondemos a P1 (índice 0)
    indice_pergunta_anterior = passo_atual - 1
    
    # Salva a resposta no array (se não for a primeira chamada)
    if passo_atual > 0 and resposta_usuario:
        # Pega o ID correto da pergunta que foi respondida
        id_pergunta_anterior = CHECKLIST_POLICIA[indice_pergunta_anterior]["id"]
        print(f"Resposta {id_pergunta_anterior}: {resposta_usuario}")
        respostas.append(f"{id_pergunta_anterior}: {resposta_usuario}")

    # Verifica se há uma PRÓXIMA pergunta
    # passo_atual é o índice da próxima pergunta (0=P1, 1=P2, ..., 6=P7)
    if passo_atual < len(CHECKLIST_POLICIA):
        # Ainda há perguntas. Vamos fazer a próxima.
        proxima_pergunta_info = CHECKLIST_POLICIA[passo_atual]
        pergunta_texto = proxima_pergunta_info["pergunta"]
        proximo_passo_num = passo_atual + 1

        response.say(pergunta_texto, language="pt-BR", voice="alice")
        response.gather(
            input="speech", language="pt-BR",
            speech_timeout="1",
            action=f"/processar_checklist_policia?passo={proximo_passo_num}" # Aponta para o próximo passo
        )
        
    else:
        # O CHECKLIST ACABOU (já respondemos P7, passo_atual é 7)
        print(f"--- [{id_chamada}] Checklist POLÍCIA Concluído ---")
        
        # PROVA DE QUE FUNCIONOU:
        print("DADOS FINAIS COLETADOS (do array global):")
        print(respostas)

        response.say("Checklist da polícia concluído. Aguarde as instruções e a chegada da viatura. Encerrando chamada.", language="pt-BR", voice="alice")
        response.hangup()
        
    # Fallback (se o usuário não responder)
    # Colocado fora do if/else para aplicar a todos os <Gather>
    if "gather" in str(response):
        response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()
         
    return Response(str(response), content_type='application/xml')

@app.route("/processar_checklist_bombeiros", methods=['POST'])
def processar_checklist_bombeiros():
    """
    PASSO 3, 4, 5...: O "Motor" do Checklist dos BOMBEIROS.
    """
    passo_atual = int(request.args.get("passo", 0))
    resposta_usuario = request.form.get('SpeechResult')
    id_chamada = request.form.get('CallSid')

    response = VoiceResponse()

    # Pega o ID da pergunta ANTERIOR (a que foi respondida)
    indice_pergunta_anterior = passo_atual - 1
    
    # Salva a resposta no array (se não for a primeira chamada)
    if passo_atual > 0 and resposta_usuario:
        # Pega o ID correto da pergunta que foi respondida
        id_pergunta_anterior = CHECKLIST_BOMBEIROS[indice_pergunta_anterior]["id"]
        print(f"Resposta {id_pergunta_anterior}: {resposta_usuario}")
        respostas.append(f"{id_pergunta_anterior}: {resposta_usuario}")

    # Verifica se há uma PRÓXIMA pergunta
    # passo_atual é o índice da próxima pergunta (0=P1, ..., 6=P7)
    if passo_atual < len(CHECKLIST_BOMBEIROS):
        # Ainda há perguntas. Vamos fazer a próxima.
        proxima_pergunta_info = CHECKLIST_BOMBEIROS[passo_atual]
        pergunta_texto = proxima_pergunta_info["pergunta"]
        proximo_passo_num = passo_atual + 1

        response.say(pergunta_texto, language="pt-BR", voice="alice")
        response.gather(
            input="speech", language="pt-BR",
            speech_timeout="1",
            action=f"/processar_checklist_bombeiros?passo={proximo_passo_num}" # Aponta para o próximo passo
        )
        
    else:
        # O CHECKLIST ACABOU (já respondemos P7, passo_atual é 7)
        print(f"--- [{id_chamada}] Checklist BOMBEIROS Concluído ---")
        
        # PROVA DE QUE FUNCIONOU:
        print("DADOS FINAIS COLETADOS (do array global):")
        print(respostas)

        response.say("Checklist dos bombeiros concluído. Mantenha a calma e siga as orientações de segurança. A equipe está a caminho. Encerrando chamada.", language="pt-BR", voice="alice")
        response.hangup()
        
    # Fallback (se o usuário não responder)
    if "gather" in str(response):
        response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()
         
    return Response(str(response), content_type='application/xml')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)