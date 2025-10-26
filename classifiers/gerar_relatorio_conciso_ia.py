import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict # Importe List e Dict

# Carrega variáveis de ambiente
load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- FUNÇÃO: GERADOR DE RELATÓRIO IA ---
def gerar_relatorio_conciso_ia(dados_brutos: List[str], categoria_emergencia: str) -> str:
    """
    Pega o array de dados brutos coletados (descrição + checklist),
    identifica a categoria da emergência e gera um relatório final conciso
    usando a OpenAI, formatado para despacho.

    Args:
        dados_brutos: Lista de strings contendo P0_descricao e as respostas P1 a P6/P7.
        categoria_emergencia: String indicando o tipo ("samu", "policia", "bombeiros").
        openai_client: A instância inicializada do cliente OpenAI.

    Returns:
        String com o relatório conciso gerado pela IA.
    """
    print(f"[IA Relatório] Gerando relatório para '{categoria_emergencia}'...")

    # Formata o array para o prompt, separando descrição inicial
    descricao_inicial = ""
    respostas_checklist_formatadas = []
    for item in dados_brutos:
        if item.startswith("P0_descricao:"):
            descricao_inicial = item.replace("P0_descricao:", "").strip()
        else:
            respostas_checklist_formatadas.append(f"- {item}") # Formata como lista

    texto_checklist = "\n".join(respostas_checklist_formatadas)

    # --- REGRA DE NEGÓCIO: O PROMPT ---
    # Define o público e o objetivo do relatório
    if categoria_emergencia == "samu":
        publico_alvo = "equipe do SAMU (paramédicos)"
        foco_principal = "estado do paciente, sintomas vitais, idade/condições, local."
    elif categoria_emergencia == "policia" or categoria_emergencia == "policia-analogia":
        publico_alvo = "equipe da POLÍCIA (viatura)"
        foco_principal = "localização, segurança, flagrante, armas, vítimas, descrição do autor."
    elif categoria_emergencia == "bombeiros":
        publico_alvo = "equipe dos BOMBEIROS"
        foco_principal = "localização, tipo de incêndio/emergência, pessoas presas, riscos (gás, eletricidade)."
    else:
        publico_alvo = "central de despacho"
        foco_principal = "resumo geral da situação."

    prompt = f"""
    Você é um assistente de despacho de emergência altamente eficiente.
    Sua tarefa é gerar um relatório EXTREMAMENTE CONCISO (máximo 4 frases curtas e diretas)
    para a {publico_alvo}, baseado nas informações coletadas por uma IA durante uma chamada.

    O objetivo é fornecer apenas os dados CRÍTICOS para a ação imediata da equipe.
    Foco principal: {foco_principal}

    INFORMAÇÕES COLETADAS:
    ---
    Descrição Inicial do Cidadão: {descricao_inicial}
    ---
    Respostas do Checklist:
    {texto_checklist}
    ---

    Gere o relatório final de despacho. Seja direto, use linguagem clara e evite informações redundantes.
    """
    # --- FIM DA REGRA DE NEGÓCIO ---

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini", # Ou outro modelo que preferir
            messages=[
                {"role": "system", "content": f"Você gera relatórios de despacho de emergência para {publico_alvo}. Seja extremamente conciso e factual."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1, # Baixa temperatura para respostas mais diretas
            max_tokens=100 # Limita o tamanho da resposta
        )
        relatorio = response.choices[0].message.content.strip()
        print(f"[IA Relatório] Relatório Gerado:\n{relatorio}")
        return relatorio

    except Exception as e:
        print(f"[IA Relatório] Erro ao gerar relatório final: {e}")
        # Fallback: retorna os dados brutos formatados em caso de erro
        return f"Erro na IA. Dados brutos:\nDescrição: {descricao_inicial}\nChecklist:\n{texto_checklist}"