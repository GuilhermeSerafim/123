import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List
import json

# Carrega variáveis de ambiente
load_dotenv()

# Inicializa cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_police_urgency(transcript: str) -> Dict[str, any]:
    """
    Classifica a urgência de uma chamada de emergência POLICIAL baseada em critérios específicos.
    
    Objetivo: proteger vidas, cessar crime, preservar local.
    ESPECÍFICO PARA EMERGÊNCIAS POLICIAIS.
    
    Args:
        transcript: Texto transcrito da chamada
        
    Returns:
        Dict com urgency_level, confidence, reasoning e extracted_info
    """
    
    prompt = f"""Você é um classificador de urgência ESPECÍFICO PARA EMERGÊNCIAS POLICIAIS. Analise o seguinte texto e extraia informações específicas para determinar o nível de urgência.

CRITÉRIOS DE ANÁLISE:

P1) O autor ainda está presente?
- Respostas: "sim, aqui perto", "não, fugiu", "não sei"
- Ação: se "sim", instruir a manter distância e buscar abrigo seguro

P2) Há armas envolvidas?
- Respostas: "arma de fogo", "arma branca", "não"
- Ação: prioridade máxima se "arma de fogo"

P3) Descreva o autor e direção de fuga
- Respostas: vestimenta, cor, altura, veículo, placa, rumo
- Ação: gerar BOLO e repassar no despacho

P4) O crime está ocorrendo agora ou acabou de ocorrer?
- Respostas: "agora", "há X minutos"
- Ação: classificar flagrante vs. atendimento posterior

P5) Há vítimas feridas?
- Respostas: "sim, sangramento", "não"
- Ação: acionar SAMU se necessário e orientar primeiros cuidados básicos

P6) Local é seguro para você falar?
- Respostas: "sim", "não, estou escondido"
- Ação: orientar silêncio, manter-se fora de vista, enviar localização

NÍVEIS DE URGÊNCIA:
- **CRÍTICA**: Arma de fogo presente + autor no local + vítimas feridas
- **ALTA**: Arma de fogo presente OU autor no local + vítimas feridas
- **MÉDIA**: Autor no local OU vítimas feridas OU crime em andamento
- **BAIXA**: Crime já ocorreu, autor fugiu, sem vítimas feridas

Texto da chamada:
"{transcript}"

Responda APENAS com um JSON válido no seguinte formato:
{{
    "urgency_level": "CRÍTICA|ALTA|MÉDIA|BAIXA",
    "confidence": numero_de_0_a_100,
    "reasoning": "explicação do nível de urgência baseado nos critérios",
    "extracted_info": {{
        "author_present": "sim|não|não_sei",
        "weapons_involved": "arma_de_fogo|arma_branca|não",
        "author_description": "descrição do autor e direção de fuga",
        "crime_timing": "agora|há_X_minutos",
        "victims_injured": "sim|não",
        "location_safe": "sim|não",
        "immediate_actions": ["lista de ações imediatas necessárias"]
    }}
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um classificador de urgência policial. Sempre retorne JSON válido."},
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
        print(f"Erro ao classificar urgência policial: {e}")
        return {
            "urgency_level": "MÉDIA",
            "confidence": 0,
            "reasoning": f"Erro no processamento: {str(e)}",
            "extracted_info": {
                "author_present": "não_sei",
                "weapons_involved": "não",
                "author_description": "não informado",
                "crime_timing": "não informado",
                "victims_injured": "não",
                "location_safe": "sim",
                "immediate_actions": ["Verificar situação"]
            }
        }

def generate_police_instructions(urgency_data: Dict[str, any]) -> str:
    """
    Gera instruções específicas para a polícia baseadas na classificação de urgência POLICIAL.
    
    Args:
        urgency_data: Dados retornados pela função classify_police_urgency
        
    Returns:
        String com instruções formatadas para despacho policial
    """
    
    urgency_level = urgency_data.get("urgency_level", "MÉDIA")
    extracted_info = urgency_data.get("extracted_info", {})
    
    instructions = []
    
    # Instruções baseadas no nível de urgência
    if urgency_level == "CRÍTICA":
        instructions.append("🚨 PRIORIDADE MÁXIMA - DESPACHO IMEDIATO")
        instructions.append("⚠️ Arma de fogo + autor presente + vítimas feridas")
        instructions.append("🔴 Equipe especializada + SAMU + isolamento da área")
    elif urgency_level == "ALTA":
        instructions.append("🚨 ALTA PRIORIDADE - DESPACHO URGENTE")
        if extracted_info.get("weapons_involved") == "arma_de_fogo":
            instructions.append("⚠️ Arma de fogo envolvida")
        if extracted_info.get("author_present") == "sim":
            instructions.append("⚠️ Autor ainda no local")
        if extracted_info.get("victims_injured") == "sim":
            instructions.append("⚠️ Vítimas feridas - acionar SAMU")
    elif urgency_level == "MÉDIA":
        instructions.append("⚡ PRIORIDADE MÉDIA - DESPACHO PADRÃO")
    else:
        instructions.append("📋 PRIORIDADE BAIXA - ATENDIMENTO POSTERIOR")
    
    # Instruções específicas baseadas nas informações extraídas
    if extracted_info.get("author_present") == "sim":
        instructions.append("👤 Autor presente - orientar vítima a manter distância")
    
    if extracted_info.get("weapons_involved") == "arma_de_fogo":
        instructions.append("🔫 Arma de fogo - equipe especializada necessária")
    
    if extracted_info.get("victims_injured") == "sim":
        instructions.append("🏥 Vítimas feridas - acionar SAMU")
    
    if extracted_info.get("location_safe") == "não":
        instructions.append("🔇 Local inseguro - orientar silêncio e abrigo")
    
    if extracted_info.get("author_description"):
        instructions.append(f"📝 Descrição do autor: {extracted_info['author_description']}")
    
    # Instruções de encerramento
    instructions.append("")
    instructions.append("📞 INSTRUÇÕES PARA A VÍTIMA:")
    instructions.append("• A equipe está a caminho")
    instructions.append("• Permaneça em local seguro")
    instructions.append("• Não confronte o autor")
    instructions.append("• Atenda o telefone de retorno")
    
    return "\n".join(instructions)
