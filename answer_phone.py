import os
import time
from flask import Flask, Response, request
from twilio.twiml.voice_response import VoiceResponse, Gather, Dial, Say
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict
import json
from twilio.rest import Client # Certifique-se que 'Client' está importado de 'twilio.rest'
from classifiers.classifier import classify_emergency_call
from classifiers.firefighter_urgency_classifier import generate_firefighter_instructions, classify_firefighter_urgency
from classifiers.police_urgency_classifier import generate_police_instructions, classify_police_urgency
from classifiers.samu_urgency_classifier import classify_samu_urgency
from classifiers.gerar_relatorio_conciso_ia import gerar_relatorio_conciso_ia

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
SIMULATION_PHONE_NUMBER = os.getenv("SIMULATION_PHONE_NUMBER")
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

CHECKLIST_SAMU = [
    # 1. Avaliação Primária (Risco imediato à vida?)
    {"id": "P1_consciencia_respiracao", "pergunta": "A pessoa está consciente e respirando?"}, # Era P2

    # 2. Localização (Para onde enviar ajuda?)
    {"id": "P2_acesso_referencia", "pergunta": "Qual o endereço completo com ponto de referência?"}, # Era P6

    # 3. Qual o problema principal?
    {"id": "P3_sintoma_principal", "pergunta": "Qual é o principal sintoma agora? Por exemplo, inconsciente, dor no peito, ou sangramento."}, # Era P1

    # 4. Há fatores agravantes óbvios?
    {"id": "P4_sangramento_fratura", "pergunta": "Há sangramento importante ou fratura aparente?"}, # Permanece P4

    # 5. Houve um mecanismo de trauma grave?
    {"id": "P5_trauma_alto_risco", "pergunta": "Houve um acidente de trânsito em alta velocidade ou queda de altura?"}, # Permanece P5

    # 6. Contexto do Paciente (modifica prioridade/cuidados)
    {"id": "P6_idade_condicoes", "pergunta": "Qual a idade aproximada e a pessoa é criança, idosa, ou gestante?"} # Era P3
]

CHECKLIST_POLICIA = [
    # 1. A pessoa pode falar?
    {"id": "P1_local_seguro", "pergunta": "O local onde você está é seguro para falar?"},
    
    # 2. Onde é a emergência? (A pergunta que você queria mover)
    {"id": "P2_acesso_referencia", "pergunta": "Qual o endereço completo com ponto de referência?"},
    
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
    {"id": "P1_acesso_referencia", "pergunta": "Qual o endereço completo com ponto de referência?"},
    {"id": "P2_tipo_emergencia", "pergunta": "O que está pegando fogo ou qual a emergência técnica? Por exemplo, residência, veículo, vazamento de gás ou queda de árvore."}, 
    {"id": "P3_pessoas_presas", "pergunta": "Há pessoas presas ou inconscientes?"}, 
    {"id": "P4_chamas_fumaca", "pergunta": "Você vê chamas, muita fumaça ou só cheiro de queimado?"},
    {"id": "P5_materiais_perigosos", "pergunta": "Há materiais perigosos no local, como botijão de gás, produtos químicos ou combustíveis?"}, 
    {"id": "P6_acesso", "pergunta": "Como é o acesso ao local? A rua é estreita ou tem algum portão trancado?"}, 
    {"id": "P7_tentativa_combate", "pergunta": "Alguém já tentou combater o fogo, por exemplo, com extintor ou mangueira?"} 
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
        response.say(f"Entendido. Vamos iniciar o checklist para o SAMU. {pergunta_p1}", language="pt-BR", voice="alice")
        
        response.gather(
            input="speech",
            language="pt-BR",
            action="/processar_checklist_samu?passo=1"
        )
        response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()
    
    elif categoria == "policia":
        pergunta_p1 = CHECKLIST_POLICIA[0]["pergunta"]
        response.say(f"Entendido. Vamos iniciar o checklist para POLICIA. {pergunta_p1}", language="pt-BR", voice="alice")
        
        response.gather(
            input="speech",
            language="pt-BR",
            action="/processar_checklist_policia?passo=1"
        )
        response.say("Não obtivemos resposta. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()
    
    elif categoria == "bombeiros":
        pergunta_p1 = CHECKLIST_BOMBEIROS[0]["pergunta"]
        response.say(f"Entendido. Vamos iniciar o checklist para os BOMBEIROS. {pergunta_p1}", language="pt-BR", voice="alice")
        
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

# (Certifique-se de que o CHECKLIST_SAMU definido no topo do seu app.py
#  seja a versão REORGANIZADA com 6 perguntas que fizemos antes)
CHECKLIST_SAMU = [
    # 1. Avaliação Primária (Risco imediato à vida?)
    {"id": "P1_consciencia_respiracao", "pergunta": "A pessoa está consciente e respirando?"}, # Era P2

    # 2. Localização (Para onde enviar ajuda?)
    {"id": "P2_acesso_referencia", "pergunta": "Qual o endereço completo com ponto de referência?"}, # Era P6

    # 3. Qual o problema principal?
    {"id": "P3_sintoma_principal", "pergunta": "Qual é o principal sintoma agora? Por exemplo, inconsciente, dor no peito, ou sangramento."}, # Era P1

    # 4. Há fatores agravantes óbvios?
    {"id": "P4_sangramento_fratura", "pergunta": "Há sangramento importante ou fratura aparente?"}, # Permanece P4

    # 5. Houve um mecanismo de trauma grave?
    {"id": "P5_trauma_alto_risco", "pergunta": "Houve um acidente de trânsito em alta velocidade ou queda de altura?"}, # Permanece P5

    # 6. Contexto do Paciente (modifica prioridade/cuidados)
    {"id": "P6_idade_condicoes", "pergunta": "Qual a idade aproximada e a pessoa é criança, idosa, ou gestante?"} # Era P3
]

# --- Rota "Motor" do Checklist (Prints Estruturados com if/elif) ---
@app.route("/processar_checklist_samu", methods=['POST'])
def processar_checklist_samu():
    """
    PASSO 3, 4, 5...: O "Motor" do Checklist.
    """
    passo_atual = int(request.args.get("passo", 0))
    resposta_usuario = request.form.get('SpeechResult')
    id_chamada = request.form.get('CallSid')

    response = VoiceResponse()

    # --- CADEIA DE PERGUNTAS COM PRINTS CORRIGIDOS ---

    if passo_atual == 1:
        # Respondeu P1 (índice 0). Vamos perguntar P2 (índice 1).
        id_pergunta_anterior = CHECKLIST_SAMU[0]["id"] # P1_consciencia_respiracao
        print(f"Resposta {id_pergunta_anterior}: {resposta_usuario}")
        respostas.append(f"{id_pergunta_anterior}: {resposta_usuario}")

        # Pergunta P2
        pergunta_p2 = CHECKLIST_SAMU[1]["pergunta"] # P2_acesso_referencia
        response.say(pergunta_p2, language="pt-BR", voice="alice")
        response.gather(
            input="speech", language="pt-BR",
            speech_timeout="1",
            action=f"/processar_checklist_samu?passo=2"
        )

    elif passo_atual == 2:
        # Respondeu P2 (índice 1). Vamos perguntar P3 (índice 2).
        id_pergunta_anterior = CHECKLIST_SAMU[1]["id"] # P2_acesso_referencia
        print(f"Resposta {id_pergunta_anterior}: {resposta_usuario}")
        respostas.append(f"{id_pergunta_anterior}: {resposta_usuario}")

        # Pergunta P3
        pergunta_p3 = CHECKLIST_SAMU[2]["pergunta"] # P3_sintoma_principal
        response.say(pergunta_p3, language="pt-BR", voice="alice")
        
        response.gather(
            input="speech", language="pt-BR",
            speech_timeout="1",
            action=f"/processar_checklist_samu?passo=3"
        )

    elif passo_atual == 3:
        # Respondeu P3 (índice 2). Vamos perguntar P4 (índice 3).
        id_pergunta_anterior = CHECKLIST_SAMU[2]["id"] # P3_sintoma_principal
        print(f"Resposta {id_pergunta_anterior}: {resposta_usuario}")
        respostas.append(f"{id_pergunta_anterior}: {resposta_usuario}")

        # Pergunta P4
        pergunta_p4 = CHECKLIST_SAMU[3]["pergunta"] # P4_sangramento_fratura
        response.say(pergunta_p4, language="pt-BR", voice="alice")
        
        response.gather(
            input="speech", language="pt-BR",
            speech_timeout="1",
            action=f"/processar_checklist_samu?passo=4"
        )

    elif passo_atual == 4:
        # Respondeu P4 (índice 3). Vamos perguntar P5 (índice 4).
        id_pergunta_anterior = CHECKLIST_SAMU[3]["id"] # P4_sangramento_fratura
        print(f"Resposta {id_pergunta_anterior}: {resposta_usuario}")
        respostas.append(f"{id_pergunta_anterior}: {resposta_usuario}")

        # Pergunta P5
        pergunta_p5 = CHECKLIST_SAMU[4]["pergunta"] # P5_trauma_alto_risco
        response.say(pergunta_p5, language="pt-BR", voice="alice")
        
        response.gather(
            input="speech", language="pt-BR",
            speech_timeout="1",
            action=f"/processar_checklist_samu?passo=5"
        )

    elif passo_atual == 5:
        # Respondeu P5 (índice 4). Vamos perguntar P6 (índice 5).
        id_pergunta_anterior = CHECKLIST_SAMU[4]["id"] # P5_trauma_alto_risco
        print(f"Resposta {id_pergunta_anterior}: {resposta_usuario}")
        respostas.append(f"{id_pergunta_anterior}: {resposta_usuario}")

        # Pergunta P6
        pergunta_p6 = CHECKLIST_SAMU[5]["pergunta"] # P6_idade_condicoes
        response.say(pergunta_p6, language="pt-BR", voice="alice")
        response.gather(
            input="speech", language="pt-BR",
            speech_timeout="1",
            action=f"/processar_checklist_samu?passo=6"
        )

    elif passo_atual == 6:
        # Respondeu P6. O CHECKLIST ACABOU.
        # (A resposta P6 já foi salva no início da função)
        print(f"--- [{id_chamada}] Checklist SAMU Concluído ---")

        # --- BABY STEP: GERAR E MOSTRAR O RELATÓRIO ---
        print("Gerando relatório final para SAMU...")
        
        # Chama a função de IA, passando o array 'respostas' e o cliente OpenAI
        relatorio_texto = gerar_relatorio_conciso_ia(respostas, "samu") 
        
        print("---- RELATÓRIO FINAL GERADO PELA IA ----")
        print(relatorio_texto)
        print("---------------------------------------")

        # --- AVISO FINAL PARA O USUÁRIO ORIGINAL ---
        # Substitua o response.say() vazio por isto:
        response.say("Checklist concluído. As equipes estão sendo acionadas. Encerrando chamada.", language="pt-BR", voice="alice")
        response.hangup() # Adiciona o comando para desligar a chamada do usuário
        # -------------------------------------------
        
        # --- FIM DO BABY STEP ---
        # --- BABY STEP: ADICIONAR O DELAY ---
        print(f"[{id_chamada}] Esperando 5 segundos antes de iniciar a simulação...")
        time.sleep(5) # <--- O DELAY DE 5 SEGUNDOS ACONTECE AQUI
        # -------------------------------------

        # --- BABY STEP: FAZER A LIGAÇÃO DE SIMULAÇÃO ---
        # 1. Constrói o TwiML que será "falado" na NOVA ligação
        twiml_para_simulacao = f"""
        <Response>
            <Say language='pt-BR' voice='alice'>
                123. Novo chamado. Relatório:
            </Say>
            <Pause length='1'/>
            <Say language='pt-BR' voice='alice'>
                {relatorio_texto}
            </Say>
            <Say language='pt-BR' voice='alice'>
                Fim do relatório. Desligando.
            </Say>
        </Response>
        """

         # 2. Tenta fazer a nova ligação usando a API REST do Twilio
        try:
            # --- BABY STEP: VERIFICAR VALORES ---
            print(f"--- [DEBUG] Iniciando Simulação ---")
            print(f"[{id_chamada}] Ligando PARA (to): {SIMULATION_PHONE_NUMBER}")
            print(f"[{id_chamada}] Ligando DE (from_): {TWILIO_NUMBER}")
            # -------------------------------------
            
            # Validação rápida (opcional, mas útil)
            if not SIMULATION_PHONE_NUMBER or not SIMULATION_PHONE_NUMBER.startswith('+'):
                print(f"[{id_chamada}] ERRO FATAL: SIMULATION_PHONE_NUMBER inválido ou não carregado: '{SIMULATION_PHONE_NUMBER}'")
                raise ValueError("Número de simulação inválido")
            if not TWILIO_NUMBER or not TWILIO_NUMBER.startswith('+'):
                 print(f"[{id_chamada}] ERRO FATAL: TWILIO_NUMBER inválido ou não carregado: '{TWILIO_NUMBER}'")
                 raise ValueError("Número Twilio (from_) inválido")

            print(f"[{id_chamada}] Acionando simulação SAMU para {SIMULATION_PHONE_NUMBER}...")
            call = twilio_client.calls.create(
                twiml=twiml_para_simulacao,     
                to=SIMULATION_PHONE_NUMBER,     
                from_=TWILIO_NUMBER             
            )
            print(f"[{id_chamada}] Simulação iniciada com SID: {call.sid}")

        except Exception as e:
            print(f"[{id_chamada}] ERRO ao iniciar simulação de chamada: {e}")
        # --- FIM DO BABY STEP ---

    else:
        # Segurança: se algo der errado (ex: passo=0 ou passo=7)
        response.say("Ocorreu um erro no checklist. Encerrando.", language="pt-BR", voice="alice")
        response.hangup()

    # Fallback (se o usuário não responder)
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