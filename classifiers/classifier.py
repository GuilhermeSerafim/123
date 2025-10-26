import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict

# Carrega variáveis de ambiente
load_dotenv()

# Inicializa cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Palavras-chave para detectar chamadas disfarçadas
DISGUISED_CALL_KEYWORDS = [
    {
        "pattern": ["pizza", "espinafre", "ketchup"],
        "description": "Pedido de pizza com ingredientes incomuns"
    }
    # Estrutura para adicionar mais padrões no futuro
]

def detect_disguised_call(transcript: str) -> Dict[str, any]:
    """
    Detecta se uma chamada é disfarçada baseada em palavras-chave específicas.
    
    Args:
        transcript: Texto transcrito da chamada
        
    Returns:
        Dict com is_disguised (bool), confidence e matched_pattern
    """
    transcript_lower = transcript.lower()
    
    for keyword_set in DISGUISED_CALL_KEYWORDS:
        pattern = keyword_set["pattern"]
        # Verifica se todas as palavras do padrão estão presentes
        if all(keyword in transcript_lower for keyword in pattern):
            return {
                "is_disguised": True,
                "confidence": 95,
                "matched_pattern": keyword_set["description"],
                "reasoning": f"Detectada chamada disfarçada com palavras-chave suspeitas: {' '.join(pattern)}"
            }
    
    return {
        "is_disguised": False,
        "confidence": 0,
        "matched_pattern": None,
        "reasoning": "Nenhum padrão de chamada disfarçada detectado"
    }

def classify_emergency_call(transcript: str) -> Dict[str, any]:
    """
    Classifica uma chamada de emergência usando OpenAI.
    
    Args:
        transcript: Texto transcrito da chamada
        
    Returns:
        Dict com category, confidence e reasoning
    """
    
    # Primeiro verifica se é uma chamada disfarçada
    disguised_check = detect_disguised_call(transcript)
    if disguised_check["is_disguised"]:
        return {
            "category": "policia-analogia",
            "confidence": disguised_check["confidence"],
            "reasoning": disguised_check["reasoning"]
        }
    
    prompt = f"""Você é um classificador de chamadas de emergência. Analise o seguinte texto transcrito de uma chamada telefônica e classifique em UMA das seguintes categorias:

1. **policia** - Crimes, violência, roubos, assaltos, brigas, ameaças
2. **samu** - Emergências médicas, acidentes com feridos, problemas de saúde
3. **bombeiros** - Incêndios, vazamentos de gás, resgates em altura, afogamentos
4. **trote** - Piadas, brincadeiras, ligações falsas com intenção de brincar, pedidos de comida/comida delivery, consultas sobre restaurantes
5. **indefinido** - Chamadas que NÃO são emergências reais MAS também NÃO são claramente trotes. Inclui: consultas genéricas, dúvidas, situações não classificáveis, contexto ambíguo, ou chamadas que não se encaixam em nenhuma categoria acima
6. **policia-analogia** - Chamadas disfarçadas onde a pessoa usa código específico para solicitar ajuda da polícia

IMPORTANTE: 
- Use "trote" para pedidos de comida, delivery, consultas sobre restaurantes ou qualquer ligação não-emergencial relacionada a comida
- Use "policia-analogia" apenas quando detectar padrões de chamada disfarçada (como pizza de espinafre com ketchup)
- Use "indefinido" apenas para situações verdadeiramente ambíguas que não se encaixam em nenhuma categoria

Texto da chamada:
"{transcript}"

Responda APENAS com um JSON válido no seguinte formato:
{{
    "category": "categoria_escolhida",
    "confidence": numero_de_0_a_100,
    "reasoning": "explicação curta do motivo da classificação"
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um classificador de emergências. Sempre retorne JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        # Extrai a resposta
        result_text = response.choices[0].message.content
        import json
        result = json.loads(result_text)
        
        return result
        
    except Exception as e:
        print(f"Erro ao classificar chamada: {e}")
        return {
            "category": "indefinido",
            "confidence": 0,
            "reasoning": f"Erro no processamento: {str(e)}"
        }
