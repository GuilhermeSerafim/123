import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List
import json

# Carrega variáveis de ambiente
load_dotenv()

# Inicializa cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_firefighter_urgency(transcript: str) -> Dict[str, any]:
    """
    Classifica a urgência de uma chamada de emergência para BOMBEIROS baseada em critérios específicos.
    
    Objetivo: eliminar risco de fogo, explosão, colapso ou aprisionamento.
    ESPECÍFICO PARA EMERGÊNCIAS DE BOMBEIROS.
    
    Args:
        transcript: Texto transcrito da chamada
        
    Returns:
        Dict com urgency_level, confidence, reasoning e extracted_info
    """
    
    prompt = f"""Você é um classificador de urgência ESPECÍFICO PARA EMERGÊNCIAS DE BOMBEIROS. Analise o seguinte texto e extraia informações específicas para determinar o nível de urgência.

CRITÉRIOS DE ANÁLISE:

P1) O que está pegando fogo ou qual a emergência técnica?
- Respostas: residência, veículo, poste, mata, indústria, vazamento de gás, queda de árvore, curto elétrico
- Ação: classificar tipo de ocorrência

P2) Há pessoas presas ou inconscientes?
- Respostas: "sim, dentro do carro/casa", "não"
- Ação: prioridade e possível apoio do SAMU e Polícia

P3) Vê chamas, muita fumaça ou só cheiro de queimado?
- Respostas: "chamas altas", "muita fumaça", "apenas cheiro"
- Ação: graduar risco e orientar evacuação

P4) Há materiais perigosos no local?
- Respostas: botijão de gás, produtos químicos, combustíveis, energia elétrica ligada
- Ação: afastar pessoas, cortar energia se seguro, evitar uso de faíscas

P5) Distância segura e rotas de acesso
- Respostas: "rua estreita", "portão trancado", "acesso por avenida X"
- Ação: orientar a liberar acesso e manter curiosos longe

P6) Alguma tentativa de combate iniciou?
- Respostas: "extintor", "mangueira", "não"
- Ação: orientar apenas se seguro, sem risco pessoal, usar extintor adequado

NÍVEIS DE URGÊNCIA:
- **CRÍTICA**: Pessoas presas + chamas altas + materiais perigosos
- **ALTA**: Pessoas presas OU chamas altas + materiais perigosos
- **MÉDIA**: Chamas visíveis OU muita fumaça OU materiais perigosos
- **BAIXA**: Apenas cheiro de queimado OU fogo pequeno sem riscos

Texto da chamada:
"{transcript}"

Responda APENAS com um JSON válido no seguinte formato:
{{
    "urgency_level": "CRÍTICA|ALTA|MÉDIA|BAIXA",
    "confidence": numero_de_0_a_100,
    "reasoning": "explicação do nível de urgência baseado nos critérios",
    "extracted_info": {{
        "emergency_type": "residência|veículo|poste|mata|indústria|vazamento_gás|queda_árvore|curto_elétrico",
        "people_trapped": "sim|não",
        "fire_visibility": "chamas_altas|muita_fumaça|apenas_cheiro",
        "dangerous_materials": "botijão_gás|produtos_químicos|combustíveis|energia_elétrica|não",
        "access_route": "rua_estreita|portão_trancado|acesso_livre",
        "combat_attempt": "extintor|mangueira|não",
        "immediate_actions": ["lista de ações imediatas necessárias"]
    }}
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um classificador de urgência para bombeiros. Sempre retorne JSON válido."},
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
        print(f"Erro ao classificar urgência de bombeiros: {e}")
        return {
            "urgency_level": "MÉDIA",
            "confidence": 0,
            "reasoning": f"Erro no processamento: {str(e)}",
            "extracted_info": {
                "emergency_type": "não_informado",
                "people_trapped": "não",
                "fire_visibility": "não_informado",
                "dangerous_materials": "não",
                "access_route": "acesso_livre",
                "combat_attempt": "não",
                "immediate_actions": ["Verificar situação"]
            }
        }

def generate_firefighter_instructions(urgency_data: Dict[str, any]) -> str:
    """
    Gera instruções específicas para os bombeiros baseadas na classificação de urgência.
    
    Args:
        urgency_data: Dados retornados pela função classify_firefighter_urgency
        
    Returns:
        String com instruções formatadas para despacho de bombeiros
    """
    
    urgency_level = urgency_data.get("urgency_level", "MÉDIA")
    extracted_info = urgency_data.get("extracted_info", {})
    
    instructions = []
    
    # Instruções baseadas no nível de urgência
    if urgency_level == "CRÍTICA":
        instructions.append("🚨 PRIORIDADE MÁXIMA - DESPACHO IMEDIATO")
        instructions.append("⚠️ Pessoas presas + chamas altas + materiais perigosos")
        instructions.append("🔴 Equipe especializada + SAMU + Polícia + isolamento da área")
    elif urgency_level == "ALTA":
        instructions.append("🚨 ALTA PRIORIDADE - DESPACHO URGENTE")
        if extracted_info.get("people_trapped") == "sim":
            instructions.append("⚠️ Pessoas presas - prioridade máxima")
        if extracted_info.get("fire_visibility") == "chamas_altas":
            instructions.append("⚠️ Chamas altas - risco de propagação")
        if extracted_info.get("dangerous_materials") != "não":
            instructions.append("⚠️ Materiais perigosos - equipe especializada")
    elif urgency_level == "MÉDIA":
        instructions.append("⚡ PRIORIDADE MÉDIA - DESPACHO PADRÃO")
    else:
        instructions.append("📋 PRIORIDADE BAIXA - ATENDIMENTO POSTERIOR")
    
    # Instruções específicas baseadas nas informações extraídas
    if extracted_info.get("people_trapped") == "sim":
        instructions.append("👥 Pessoas presas - acionar SAMU e Polícia")
    
    if extracted_info.get("fire_visibility") == "chamas_altas":
        instructions.append("🔥 Chamas altas - risco de propagação")
    elif extracted_info.get("fire_visibility") == "muita_fumaça":
        instructions.append("💨 Muita fumaça - orientar evacuação")
    
    if extracted_info.get("dangerous_materials") == "botijão_gás":
        instructions.append("⛽ Botijão de gás - risco de explosão")
    elif extracted_info.get("dangerous_materials") == "produtos_químicos":
        instructions.append("🧪 Produtos químicos - equipe especializada")
    elif extracted_info.get("dangerous_materials") == "energia_elétrica":
        instructions.append("⚡ Energia elétrica - cortar energia se seguro")
    
    if extracted_info.get("access_route") == "rua_estreita":
        instructions.append("🚗 Rua estreita - orientar liberação de acesso")
    elif extracted_info.get("access_route") == "portão_trancado":
        instructions.append("🚪 Portão trancado - orientar abertura")
    
    if extracted_info.get("combat_attempt") == "extintor":
        instructions.append("🧯 Tentativa com extintor - orientar apenas se seguro")
    elif extracted_info.get("combat_attempt") == "mangueira":
        instructions.append("🚰 Tentativa com mangueira - orientar apenas se seguro")
    
    # Instruções de encerramento
    instructions.append("")
    instructions.append("📞 INSTRUÇÕES PARA A VÍTIMA:")
    instructions.append("• Evacue a área imediatamente")
    instructions.append("• Não volte para buscar objetos")
    instructions.append("• Aguarde os bombeiros em local seguro e visível")
    instructions.append("• Mantenha curiosos longe da área")
    
    return "\n".join(instructions)
