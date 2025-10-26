# 📞 Assistente de Atendimento Emergencial Unificado com IA

## 📝 Descrição

Este projeto implementa um sistema de atendimento telefônico unificado para emergências (similar a um 911 ou 190/192/193 centralizado) que utiliza Inteligência Artificial para:

1.  **Classificar** a natureza da emergência (SAMU, Polícia, Bombeiros) com base na descrição inicial do cidadão.
2.  **Conduzir** um checklist interativo e dinâmico por voz para coletar informações cruciais de forma padronizada.
3.  **Gerar** um relatório conciso e estruturado com os dados coletados.
4.  **(Simulação)** Realizar uma chamada telefônica para um número pré-definido, "lendo" o relatório gerado, simulando o despacho da ocorrência para o departamento responsável.

## 🎯 Objetivo

O objetivo principal é otimizar o atendimento inicial de emergências, reduzindo o tempo de resposta, diminuindo a carga cognitiva sobre o cidadão em pânico (que não precisa saber qual número discar) e fornecendo informações mais estruturadas para as equipes de despacho, potencialmente salvando vidas.

## ✨ Funcionalidades Principais

* **Número Único:** Recebe chamadas em um único número de telefone configurado via Twilio.
* **Transcrição em Tempo Real:** Utiliza o `<Gather>` do Twilio para transcrever a fala do usuário.
* **Classificação Nível 1 (IA):** Usa a API da OpenAI (GPT-4o mini) para interpretar a descrição inicial e direcionar para o checklist correto (SAMU, Polícia, Bombeiros).
* **Checklists Interativos (IA + Lógica):** Conduz uma série de perguntas e respostas por voz, guiadas pela categoria da emergência, para coletar dados essenciais.
* **Geração de Relatório Nível 2 (IA):** Ao final do checklist, usa a API da OpenAI para sumarizar todas as informações coletadas em um relatório breve e objetivo.
* **Simulação de Despacho:** Utiliza a API REST do Twilio para realizar uma nova chamada para um número configurado, usando Text-to-Speech (`<Say>`) para vocalizar o relatório gerado.
* **Tratamento Básico de Erros:** Lida com falhas na transcrição ou fluxos inesperados.

## ⚙️ Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Framework Web:** Flask (para receber os webhooks do Twilio)
* **Telefonia e Voz:** Twilio (API de Voz, TwiML `<Gather>`, `<Say>`, `<Hangup>`, API REST `calls.create`)
* **Inteligência Artificial:** OpenAI API (GPT-4o mini ou similar)
* **Variáveis de Ambiente:** python-dotenv
* **Túnel Local (Desenvolvimento):** Ngrok

## 🚀 Como Funciona (Fluxo Simplificado)

1.  **Chamada Recebida:** Cidadão liga para o número Twilio configurado.
2.  **Webhook Inicial (`/`):** Twilio chama a rota `/` do Flask. O Flask responde com TwiML para dizer "Fale sua emergência" e ouvir (`<Gather>`).
3.  **Primeira Transcrição (`/receber_transcricao`):** Twilio envia o texto transcrito para esta rota.
4.  **Classificação Nv1:** A função `classify_emergency_call` (usando OpenAI) determina a categoria (SAMU, Polícia, etc.).
5.  **Início do Checklist:** O Flask responde com TwiML contendo a primeira pergunta do checklist apropriado e um `<Gather>` apontando para a rota do "motor" do checklist (ex: `/processar_checklist_samu?passo=1`).
6.  **Loop do Checklist (`/processar_checklist_...`):**
    * Twilio envia a resposta do usuário para a rota do motor, junto com o `passo` atual.
    * O Flask salva a resposta (no array `respostas` no MVP).
    * O Flask pega a *próxima* pergunta do checklist.
    * O Flask responde com TwiML contendo a próxima pergunta e um `<Gather>` apontando de volta para a mesma rota, mas com o `passo` incrementado.
    * Isso se repete até a última pergunta.
7.  **Fim do Checklist:** Ao receber a resposta da última pergunta, a rota do motor:
    * Salva a resposta final.
    * Chama `gerar_relatorio_conciso_ia` (usando OpenAI) para criar o sumário.
    * Responde ao Twilio com TwiML para avisar o usuário e desligar (`<Hangup>`) a chamada *original*.
    * **Simulação:** Usa a API REST do Twilio (`twilio_client.calls.create`) para fazer uma *nova* ligação para o `SIMULATION_PHONE_NUMBER`, passando um TwiML que "fala" o relatório gerado.

## 🔧 Configuração

O projeto utiliza variáveis de ambiente para configurar as chaves de API e números de telefone. Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```dotenv
# Chave da API da OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Credenciais da Conta Twilio (Account SID e Auth Token)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Número de telefone comprado/configurado no Twilio (formato E.164)
TWILIO_NUMBER=+1xxxxxxxxxx

# Número de telefone para receber a ligação de simulação (formato E.164)
# (Deve ser um número verificado na sua conta Twilio Trial)
SIMULATION_PHONE_NUMBER=+55xxxxxxxxxxx
