import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict

# Carrega variáveis de ambiente
load_dotenv()

# Inicializa cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_emergency_call(transcript: str) -> Dict[str, any]:
    """
    Classifica uma chamada de emergência usando OpenAI.
    
    Args:
        transcript: Texto transcrito da chamada
        
    Returns:
        Dict com category, confidence e reasoning
    """
    
    prompt = f"""Você é um classificador de chamadas de emergência. Analise o seguinte texto transcrito de uma chamada telefônica e classifique em UMA das seguintes categorias:

1. **policia** - Crimes, violência, roubos, assaltos, brigas, ameaças
2. **samu** - Emergências médicas, acidentes com feridos, problemas de saúde
3. **bombeiros** - Incêndios, vazamentos de gás, resgates em altura, afogamentos
4. **trote** - Apenas para piadas claras, brincadeiras explícitas, ligações obviamente falsas com intenção de brincar
5. **indefinido** - Chamadas que NÃO são emergências reais MAS também NÃO são claramente trotes. Inclui: consultas genéricas, dúvidas, situações não classificáveis, contexto ambíguo, ou chamadas que não se encaixam em nenhuma categoria acima

IMPORTANTE: Use "indefinido" quando a chamada não é emergência e não é claramente um trote proposital. Use "trote" apenas quando houver intenção clara de fazer uma piada.

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
