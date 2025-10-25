# 🚨 Unificador de Emergência

Sistema inteligente de classificação automática de chamadas de emergência que direciona automaticamente para o serviço correto (Polícia, SAMU, Bombeiros) usando inteligência artificial.

## 🎯 Objetivo

Este projeto visa criar um sistema unificado que:
- Recebe chamadas de emergência
- Classifica automaticamente a natureza da emergência
- Direciona para o serviço apropriado (190, 192, 193)
- Reduz tempo de resposta e melhora eficiência dos serviços de emergência

## 🏷️ Categorias de Classificação

- **🚔 policia**: Crimes, violência, roubos, assaltos, brigas
- **🚑 samu**: Emergências médicas, acidentes com feridos
- **🚒 bombeiros**: Incêndios, vazamentos de gás, resgates
- **🎭 trote**: Chamadas falsas ou piadas
- **❓ indefinido**: Contexto ambíguo ou não classificável

## 🚀 Instalação

### Pré-requisitos
- Python 3.8+
- Conta OpenAI
- (Opcional) Conta Twilio para chamadas reais

### Passo a passo

1. **Clone o repositório:**
```bash
git clone https://github.com/djairofilho/unificador-de-emergencia.git
cd unificador-de-emergencia
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente:**
```bash
# Copie o arquivo de exemplo
cp env.example .env

# Edite o arquivo .env com suas credenciais
# OPENAI_API_KEY=sua_chave_da_openai_aqui
```

4. **Teste o sistema:**
```bash
python test_classifier.py
```

## 📖 Como Usar

### 1. 🧪 Teste com dados mockados

Execute o script de teste para ver exemplos de classificação:
```bash
python test_classifier.py
```

Este script testa 10 exemplos pré-definidos e mostra a classificação de cada um.

### 2. 🌐 Teste via API

Inicie o servidor:
```bash
python app.py
```

Teste a classificação via API:
```bash
curl -X POST "http://localhost:5000/classify" \
  -H "Content-Type: application/json" \
  -d '{"text": "Tem um incêndio no meu prédio! Venham rápido!"}'
```

**Resposta esperada:**
```json
{
  "category": "bombeiros",
  "confidence": 95,
  "reasoning": "Texto menciona claramente 'incêndio' e 'prédio', indicando necessidade dos bombeiros"
}
```

### 3. 📞 Uso com chamadas reais (Twilio)

O sistema está integrado com Twilio para chamadas reais:
1. **Recebe chamada** → Grava áudio
2. **Transcreve** → Converte áudio em texto
3. **Classifica** → IA determina categoria
4. **Direciona** → Envia para serviço correto

**Endpoints disponíveis:**
- `POST /voice` - Recebe chamadas
- `POST /handle_recording` - Processa gravações
- `POST /classify` - Classifica textos

## 📁 Estrutura do Projeto

```
unificador-de-emergencia/
├── app.py              # 🚀 API FastAPI com endpoints
├── classifier.py       # 🧠 Lógica de classificação com OpenAI
├── test_classifier.py  # 🧪 Script de teste com dados mockados
├── requirements.txt    # 📦 Dependências do projeto
├── env.example        # 🔧 Exemplo de variáveis de ambiente
├── .gitignore         # 🚫 Arquivos ignorados pelo Git
└── README.md          # 📖 Este arquivo
```

## 🔧 Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido
- **OpenAI GPT-4o-mini** - Modelo de IA para classificação
- **Twilio** - Integração com chamadas telefônicas
- **Python 3.8+** - Linguagem de programação

## ⚙️ Configurações Técnicas

- **Modelo OpenAI**: `gpt-4o-mini`
- **Temperature**: 0.3 (respostas consistentes)
- **Formato**: JSON estruturado com categoria, confiança e raciocínio

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

**Djairo Filho**
- GitHub: [@djairofilho](https://github.com/djairofilho)
