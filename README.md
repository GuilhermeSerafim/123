# 📞 Assistente de Atendimento Emergencial Unificado com IA

> **Protótipo em desenvolvimento.** O fluxo descrito abaixo representa a intenção do projeto; esta versão não está validada para atendimento real nem para despacho de equipes.

## Estado da implementação

`answer_phone.py` e `requirements.txt` apresentam os seguintes limites:

- O código importa Flask, mas o manifesto não lista essa dependência. Também importa `classifiers.firefighter_urgency_classifier`, `classifiers.police_urgency_classifier` e `classifiers.samu_urgency_classifier`, ausentes do repositório.
- A lista `respostas` é global e compartilhada entre os fluxos de chamadas.
- O encerramento do checklist SAMU chama a geração do relatório e `twilio_client.calls.create`; os encerramentos de Polícia e Bombeiros não implementam esse mesmo despacho em `answer_phone.py`.
- A etapa chamada de “simulação” usa telefonia real para o número configurado. Há também um fallback `response.dial("190")`; portanto, executar o fluxo sem revisão não é um teste isolado.

Antes de executar, resolver esses pontos e validar o fluxo com mocks, sem discagem ou envio de dados reais. A configuração abaixo não resolve as dependências e os módulos ausentes.


## 📝 Descrição

Este projeto explora um sistema de atendimento telefônico unificado para emergências (similar a um 911 ou 190/192/193 centralizado) que utiliza Inteligência Artificial para:

1.  **Classificar** a natureza da emergência (SAMU, Polícia, Bombeiros) com base na descrição inicial do cidadão.
2.  **Conduzir** um checklist interativo e dinâmico por voz para coletar informações cruciais de forma padronizada.
3.  **Gerar**, no checklist SAMU, um relatório conciso e estruturado com os dados coletados.
4.  **Chamada de demonstração do SAMU:** realizar uma chamada real para um número configurado, lendo o relatório gerado. O mesmo fechamento não está implementado nos checklists de Polícia e Bombeiros.

## 🎯 Objetivo

Explorar a coleta estruturada de informações por voz em um protótipo de atendimento. O projeto não substitui os serviços de emergência.

## ✨ Funcionalidades pretendidas e componentes do protótipo

* **Número Único:** Recebe chamadas em um único número de telefone configurado via Twilio.
* **Transcrição em Tempo Real:** Utiliza o `<Gather>` do Twilio para transcrever a fala do usuário.
* **Classificação Nível 1 (IA):** Usa a API da OpenAI (GPT-4o mini) para interpretar a descrição inicial e direcionar para o checklist correto (SAMU, Polícia, Bombeiros).
* **Checklists Interativos (IA + Lógica):** Conduz uma série de perguntas e respostas por voz, guiadas pela categoria da emergência, para coletar dados essenciais.
* **Geração de Relatório Nível 2 (IA):** Ao final do checklist SAMU, usa a API da OpenAI para sumarizar todas as informações coletadas em um relatório breve e objetivo.
* **Chamada de demonstração do SAMU:** Utiliza a API REST do Twilio para realizar uma nova chamada real para um número configurado, usando Text-to-Speech (`<Say>`) para vocalizar o relatório gerado.
* **Tratamento Básico de Erros:** Lida com falhas na transcrição ou fluxos inesperados.

## ⚙️ Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Framework Web:** Flask (para receber os webhooks do Twilio)
* **Telefonia e Voz:** Twilio (API de Voz, TwiML `<Gather>`, `<Say>`, `<Hangup>`, API REST `calls.create`)
* **Inteligência Artificial:** OpenAI API (GPT-4o mini ou similar)
* **Variáveis de Ambiente:** python-dotenv
* **Túnel Local (Desenvolvimento):** Ngrok

## 🚀 Fluxo pretendido (com limitações descritas acima)

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
7.  **Fim do checklist SAMU:** Ao receber a resposta da última pergunta, a rota do SAMU:
    * Salva a resposta final.
    * Chama `gerar_relatorio_conciso_ia` (usando OpenAI) para criar o sumário.
    * Responde ao Twilio com TwiML para avisar o usuário e desligar (`<Hangup>`) a chamada *original*.
    * **Chamada real de demonstração:** Usa a API REST do Twilio (`twilio_client.calls.create`) para fazer uma *nova* ligação para o `SIMULATION_PHONE_NUMBER`, passando um TwiML que "fala" o relatório gerado.

Polícia e Bombeiros têm checklists próprios, mas não implementam essa geração de relatório e chamada de saída no fechamento.

## 🔧 Configuração

O projeto utiliza variáveis de ambiente para configurar as chaves de API e números de telefone. O modelo abaixo lista as variáveis para um arquivo `.env` na raiz. Os campos estão vazios; mantenha credenciais fora do versionamento e use mocks durante o desenvolvimento:

```dotenv
# Chave da API da OpenAI
OPENAI_API_KEY=

# Credenciais da Conta Twilio (Account SID e Auth Token)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=

# Número de telefone comprado/configurado no Twilio (formato E.164)
TWILIO_NUMBER=

# Número de telefone para receber a chamada real de demonstração (formato E.164)
# (Deve ser um número verificado na sua conta Twilio Trial)
SIMULATION_PHONE_NUMBER=

```
