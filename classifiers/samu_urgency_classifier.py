import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List
import json

# Carrega variáveis de ambiente
load_dotenv()

# Inicializa cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_samu_urgency(transcript: str) -> Dict[str, any]:
    """
    Classifica a urgência de uma chamada de emergência para SAMU baseada em critérios específicos.
    
    Objetivo: estabilizar até a chegada da equipe.
    ESPECÍFICO PARA EMERGÊNCIAS MÉDICAS (SAMU).
    
    Args:
        transcript: Texto transcrito da chamada
        
    Returns:
        Dict com urgency_level, confidence, reasoning e extracted_info
    """
    
    prompt = f"""Você é um classificador de urgência ESPECÍFICO PARA EMERGÊNCIAS MÉDICAS (SAMU). Analise o seguinte texto e extraia informações específicas para determinar o nível de urgência.

CRITÉRIOS DE ANÁLISE:

P1) Qual é o principal sintoma agora?
- Respostas: inconsciente, não respira, convulsão, dor no peito, sangramento intenso, engasgo, trauma, parto
- Ação: escolher protocolo de suporte imediato

P2) A pessoa está consciente e respirando?
- Respostas: "consciente e respira", "inconsciente e não respira", "inconsciente e respira"
- Ação:
  - Não respira: iniciar RCP guiada
  - Respira mas inconsciente: posição lateral de segurança
  - Convulsão: proteger cabeça, não conter

P3) Idade aproximada e condições especiais
- Respostas: criança, idoso, gestante, comorbidades, uso de anticoagulante
- Ação: ajustar prioridade e cuidados

P4) Há sangramento importante ou fratura aparente?
- Respostas: "sim, muito sangue", "fratura exposta", "não"
- Ação: compressão direta, elevação de membro se possível, não realinhar fraturas

P5) Trauma de alto risco ou queda de altura?
- Respostas: "acidente de trânsito alta velocidade", "queda de 3 m+", "não"
- Ação: evitar movimentar, estabilizar cabeça, aguardar equipe

P6) Acesso e referência visual
- Respostas: "portaria, bloco, ponto de referência", "cadeado"
- Ação: organizar recepção para agilizar atendimento

NÍVEIS DE URGÊNCIA:
- **CRÍTICA**: Não respira OU inconsciente + trauma alto risco + sangramento intenso
- **ALTA**: Inconsciente + respira OU convulsão + sangramento OU trauma alto risco
- **MÉDIA**: Consciente + sintomas graves OU sangramento moderado OU trauma
- **BAIXA**: Consciente + sintomas leves OU consulta médica

Texto da chamada:
"{transcript}"

Responda APENAS com um JSON válido no seguinte formato:
{{
    "urgency_level": "CRÍTICA|ALTA|MÉDIA|BAIXA",
    "confidence": numero_de_0_a_100,
    "reasoning": "explicação do nível de urgência baseado nos critérios",
    "extracted_info": {{
        "main_symptom": "inconsciente|não_respira|convulsão|dor_peito|sangramento_intenso|engasgo|trauma|parto",
        "consciousness_breathing": "consciente_respira|inconsciente_não_respira|inconsciente_respira",
        "age_conditions": "criança|idoso|gestante|comorbidades|anticoagulante|adulto_saudável",
        "bleeding_fracture": "sangramento_intenso|fratura_exposta|sangramento_moderado|não",
        "high_risk_trauma": "acidente_alta_velocidade|queda_altura|trauma_leve|não",
        "access_reference": "portaria_bloco|ponto_referência|cadeado|acesso_livre",
        "immediate_actions": ["lista de ações imediatas necessárias"]
    }}
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um classificador de urgência médica para SAMU. Sempre retorne JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        # Extrai a resposta
        result_text = response.choices[0].message.content
        result = json.loads(result_text)
        
        return result
        
    except Exception as e:
        print(f"Erro ao classificar urgência do SAMU: {e}")
        return {
            "urgency_level": "MÉDIA",
            "confidence": 0,
            "reasoning": f"Erro no processamento: {str(e)}",
            "extracted_info": {
                "main_symptom": "não_informado",
                "consciousness_breathing": "consciente_respira",
                "age_conditions": "adulto_saudável",
                "bleeding_fracture": "não",
                "high_risk_trauma": "não",
                "access_reference": "acesso_livre",
                "immediate_actions": ["Verificar situação"]
            }
        }

def generate_samu_instructions(urgency_data: Dict[str, any]) -> str:
    """
    Gera instruções específicas para o SAMU baseadas na classificação de urgência.
    
    Args:
        urgency_data: Dados retornados pela função classify_samu_urgency
        
    Returns:
        String com instruções formatadas para despacho do SAMU
    """
    
    urgency_level = urgency_data.get("urgency_level", "MÉDIA")
    extracted_info = urgency_data.get("extracted_info", {})
    
    instructions = []
    
    # Instruções baseadas no nível de urgência
    if urgency_level == "CRÍTICA":
        instructions.append("🚨 PRIORIDADE MÁXIMA - DESPACHO IMEDIATO")
        instructions.append("⚠️ Não respira OU inconsciente + trauma alto risco + sangramento intenso")
        instructions.append("🔴 Equipe especializada + RCP guiada + estabilização")
    elif urgency_level == "ALTA":
        instructions.append("🚨 ALTA PRIORIDADE - DESPACHO URGENTE")
        if extracted_info.get("consciousness_breathing") == "inconsciente_não_respira":
            instructions.append("⚠️ Não respira - iniciar RCP guiada")
        if extracted_info.get("main_symptom") == "convulsão":
            instructions.append("⚠️ Convulsão - proteger cabeça")
        if extracted_info.get("bleeding_fracture") in ["sangramento_intenso", "fratura_exposta"]:
            instructions.append("⚠️ Sangramento/fratura - compressão direta")
    elif urgency_level == "MÉDIA":
        instructions.append("⚡ PRIORIDADE MÉDIA - DESPACHO PADRÃO")
    else:
        instructions.append("📋 PRIORIDADE BAIXA - ATENDIMENTO POSTERIOR")
    
    # Instruções específicas baseadas nas informações extraídas
    if extracted_info.get("consciousness_breathing") == "inconsciente_não_respira":
        instructions.append("🫁 Não respira - INICIAR RCP GUIADA IMEDIATAMENTE")
    elif extracted_info.get("consciousness_breathing") == "inconsciente_respira":
        instructions.append("🛌 Inconsciente mas respira - posição lateral de segurança")
    
    if extracted_info.get("main_symptom") == "convulsão":
        instructions.append("🧠 Convulsão - proteger cabeça, NÃO conter movimentos")
    
    if extracted_info.get("main_symptom") == "dor_peito":
        instructions.append("❤️ Dor no peito - posição confortável, monitorar sinais vitais")
    
    if extracted_info.get("bleeding_fracture") == "sangramento_intenso":
        instructions.append("🩸 Sangramento intenso - compressão direta + elevação do membro")
    elif extracted_info.get("bleeding_fracture") == "fratura_exposta":
        instructions.append("🦴 Fratura exposta - NÃO realinhar, cobrir com pano limpo")
    
    if extracted_info.get("high_risk_trauma") in ["acidente_alta_velocidade", "queda_altura"]:
        instructions.append("🚗 Trauma alto risco - NÃO movimentar, estabilizar cabeça")
    
    if extracted_info.get("age_conditions") == "criança":
        instructions.append("👶 Criança - cuidados pediátricos especiais")
    elif extracted_info.get("age_conditions") == "idoso":
        instructions.append("👴 Idoso - atenção a comorbidades")
    elif extracted_info.get("age_conditions") == "gestante":
        instructions.append("🤰 Gestante - cuidados obstétricos")
    
    if extracted_info.get("access_reference") == "cadeado":
        instructions.append("🔒 Acesso com cadeado - orientar abertura para equipe")
    
    # Instruções de encerramento
    instructions.append("")
    instructions.append("📞 INSTRUÇÕES PARA A VÍTIMA/FAMILIAR:")
    instructions.append("• Permaneça na linha se precisar de instruções")
    instructions.append("• Mantenha o paciente aquecido")
    instructions.append("• NÃO ofereça líquidos")
    instructions.append("• A equipe está a caminho")
    
    return "\n".join(instructions)
