# 🚨 Sistema de Classificação de Urgência POLICIAL

Sistema inteligente ESPECÍFICO PARA POLÍCIA para classificar a urgência de chamadas de emergência policial, com foco em **proteger vidas, cessar crimes e preservar locais**.

## 🎯 Objetivo

Classificar automaticamente a urgência de chamadas de emergência baseado em critérios específicos para otimizar o despacho policial.

## 📋 Critérios de Análise

### P1) O autor ainda está presente?
- **Respostas**: "sim, aqui perto", "não, fugiu", "não sei"
- **Ação**: se "sim", instruir a manter distância e buscar abrigo seguro

### P2) Há armas envolvidas?
- **Respostas**: "arma de fogo", "arma branca", "não"
- **Ação**: prioridade máxima se "arma de fogo"

### P3) Descreva o autor e direção de fuga
- **Respostas**: vestimenta, cor, altura, veículo, placa, rumo
- **Ação**: gerar BOLO e repassar no despacho

### P4) O crime está ocorrendo agora ou acabou de ocorrer?
- **Respostas**: "agora", "há X minutos"
- **Ação**: classificar flagrante vs. atendimento posterior

### P5) Há vítimas feridas?
- **Respostas**: "sim, sangramento", "não"
- **Ação**: acionar SAMU se necessário e orientar primeiros cuidados básicos

### P6) Local é seguro para você falar?
- **Respostas**: "sim", "não, estou escondido"
- **Ação**: orientar silêncio, manter-se fora de vista, enviar localização

## 🚨 Níveis de Urgência

| Nível | Critérios | Ação |
|-------|-----------|------|
| **CRÍTICA** | Arma de fogo + autor no local + vítimas feridas | Despacho imediato + equipe especializada + SAMU |
| **ALTA** | Arma de fogo OU autor no local + vítimas feridas | Despacho urgente + recursos especiais |
| **MÉDIA** | Autor no local OU vítimas feridas OU crime em andamento | Despacho padrão |
| **BAIXA** | Crime já ocorreu, autor fugiu, sem vítimas feridas | Atendimento posterior |

## 🔧 Como Usar

### 1. Teste Manual
```bash
python test_urgency_classifier.py
```

### 2. API Endpoints

#### Classificar Urgência POLICIAL
```bash
curl -X POST "http://localhost:5000/classify-police-urgency" \
  -H "Content-Type: application/json" \
  -d '{"text": "Tem um homem armado aqui na minha casa, ele ainda está aqui!"}'
```

#### Resposta da API
```json
{
  "police_urgency_analysis": {
    "urgency_level": "CRÍTICA",
    "confidence": 95,
    "reasoning": "Arma de fogo presente + autor no local + vítimas feridas",
    "extracted_info": {
      "author_present": "sim",
      "weapons_involved": "arma_de_fogo",
      "author_description": "homem armado",
      "crime_timing": "agora",
      "victims_injured": "sim",
      "location_safe": "não",
      "immediate_actions": ["Despacho imediato", "Equipe especializada", "SAMU"]
    }
  },
  "police_instructions": "🚨 PRIORIDADE MÁXIMA - DESPACHO IMEDIATO\n⚠️ Arma de fogo + autor presente + vítimas feridas\n🔴 Equipe especializada + SAMU + isolamento da área\n..."
}
```

## 📁 Arquivos

- `urgency_classifier.py` - Classificador principal
- `test_urgency_classifier.py` - Testes automatizados
- `app.py` - API FastAPI integrada
- `README_URGENCY.md` - Esta documentação

## 🚀 Integração com Sistema Principal

O classificador de urgência é automaticamente ativado quando:
- A classificação inicial retorna `policia` ou `policia-analogia`
- Gera instruções específicas para despacho
- Registra logs detalhados para análise

## 📊 Exemplo de Saída

```
🚨 Análise de Urgência:
   Nível: CRÍTICA
   Confiança: 95%
   Motivo: Arma de fogo presente + autor no local + vítimas feridas

📋 Instruções para Despacho:
🚨 PRIORIDADE MÁXIMA - DESPACHO IMEDIATO
⚠️ Arma de fogo + autor presente + vítimas feridas
🔴 Equipe especializada + SAMU + isolamento da área
👤 Autor presente - orientar vítima a manter distância
🔫 Arma de fogo - equipe especializada necessária
🏥 Vítimas feridas - acionar SAMU
🔇 Local inseguro - orientar silêncio e abrigo

📞 INSTRUÇÕES PARA A VÍTIMA:
• A equipe está a caminho
• Permaneça em local seguro
• Não confronte o autor
• Atenda o telefone de retorno
```

## 🔄 Fluxo Completo

1. **Chamada recebida** → Transcrição automática
2. **Classificação inicial** → Categoria (policia, samu, bombeiros, etc.)
3. **Se policial** → Análise de urgência automática
4. **Geração de instruções** → Despacho otimizado
5. **Logs detalhados** → Análise e melhoria contínua
