# Sistema Unificador de Emergência

Sistema inteligente de classificação automática de chamadas de emergência que direciona automaticamente para o serviço correto (Polícia, SAMU, Bombeiros) usando inteligência artificial.

## Visão Geral

Este projeto visa criar um sistema unificado que:
- Recebe chamadas de emergência
- Classifica automaticamente a natureza da emergência
- Direciona para o serviço apropriado (190, 192, 193)
- Reduz tempo de resposta e melhora eficiência dos serviços de emergência

## Categorias de Classificação

- **Polícia**: Crimes, violência, roubos, assaltos, brigas
- **SAMU**: Emergências médicas, acidentes com feridos
- **Bombeiros**: Incêndios, vazamentos de gás, resgates
- **Trote**: Chamadas falsas ou piadas
- **Indefinido**: Contexto ambíguo ou não classificável

## Instalação

### Pré-requisitos
- Python 3.8 ou superior
- Conta OpenAI com API Key válida
- (Opcional) Conta Twilio para chamadas telefônicas reais
- 4GB RAM mínimo (recomendado 8GB)
- Conexão com internet para API OpenAI

### Passo a passo

1. **Clone o repositório:**
```bash
git clone https://github.com/djairofilho/unificador-de-emergencia.git
cd unificador-de-emergencia
```

2. **Crie um ambiente virtual:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente:**
```bash
# Crie um arquivo .env na raiz do projeto
echo "OPENAI_API_KEY=sua_chave_da_openai_aqui" > .env
```

5. **Teste o sistema:**
```bash
python tests/run_all_tests.py
```

## Como Usar

### 1. Teste com dados mockados

Execute todos os testes do sistema:
```bash
python tests/run_all_tests.py
```

Ou execute testes específicos:
```bash
# Teste de classificação geral
python tests/test_classifier.py

# Teste de urgência policial
python tests/test_police_urgency_classifier.py

# Teste de urgência de bombeiros
python tests/test_firefighter_urgency_classifier.py

# Teste de urgência do SAMU
python tests/test_samu_urgency_classifier.py

# Teste de polícia analogia
python tests/test_policia_analogia.py
```

### 2. Teste via API

Inicie o servidor:
```bash
python app.py
```

O servidor estará disponível em `http://localhost:5000`

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

### 3. Executar com Uvicorn (Produção)

Para executar em modo de produção:
```bash
uvicorn app:app --host 0.0.0.0 --port 5000 --reload
```

### 4. Uso com chamadas reais (Twilio)

O sistema está integrado com Twilio para chamadas reais:
1. **Recebe chamada** → Grava áudio
2. **Transcreve** → Converte áudio em texto
3. **Classifica** → IA determina categoria
4. **Direciona** → Envia para serviço correto

**Endpoints disponíveis:**

- `GET /` - Página inicial (demo)
- `POST /voice` - Recebe chamadas telefônicas
- `POST /handle_recording` - Processa gravações de áudio
- `POST /classify` - Classifica textos de emergência
- `POST /classify-police-urgency` - Classifica urgência POLICIAL
- `POST /classify-firefighter-urgency` - Classifica urgência de BOMBEIROS
- `POST /classify-samu-urgency` - Classifica urgência do SAMU

**Documentação da API:**
Quando o servidor estiver rodando, acesse `http://localhost:5000/docs` para ver a documentação interativa da API (Swagger UI).

## Estrutura do Projeto

```
Classificador/
├── app.py                    # API FastAPI com endpoints
├── answer_phone.py          # Versão Flask (legado)
├── requirements.txt         # Dependências do projeto
├── LICENSE                  # Licença MIT
├── classifiers/             # Pasta de classificadores organizados
│   ├── __init__.py
│   ├── classifier.py        # Classificador geral de emergências
│   ├── police_urgency_classifier.py # Classificador de urgência POLICIAL
│   ├── firefighter_urgency_classifier.py  # Classificador de urgência de BOMBEIROS
│   ├── samu_urgency_classifier.py         # Classificador de urgência do SAMU
│   └── README.md            # Documentação dos classificadores
├── tests/                   # Pasta de testes organizados
│   ├── __init__.py
│   ├── run_all_tests.py     # Executa todos os testes
│   ├── test_classifier.py   # Teste de classificação geral
│   ├── test_police_urgency_classifier.py  # Teste de urgência policial
│   ├── test_firefighter_urgency_classifier.py  # Teste de urgência de bombeiros
│   ├── test_samu_urgency_classifier.py         # Teste de urgência do SAMU
│   ├── test_policia_analogia.py   # Teste de chamadas disfarçadas
│   └── README.md            # Documentação dos testes
├── README.md                # Documentação principal
└── venv/                   # Ambiente virtual Python
```

## Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido para APIs
- **OpenAI GPT-4o-mini** - Modelo de IA para classificação inteligente
- **Twilio** - Integração com chamadas telefônicas e SMS
- **Uvicorn** - Servidor ASGI para aplicações FastAPI
- **Pydantic** - Validação de dados e serialização
- **Python 3.8+** - Linguagem de programação principal

### Dependências Principais

- `fastapi==0.120.0` - Framework web
- `openai==2.6.1` - Cliente OpenAI
- `twilio==9.8.4` - SDK Twilio
- `uvicorn==0.38.0` - Servidor ASGI
- `pydantic==2.12.3` - Validação de dados
- `python-dotenv==1.1.1` - Gerenciamento de variáveis de ambiente

## Configurações Técnicas

- **Modelo OpenAI**: `gpt-4o-mini`
- **Temperature**: 0.3 (respostas consistentes e determinísticas)
- **Formato de Resposta**: JSON estruturado com categoria, confiança e raciocínio
- **Porta do Servidor**: 5000 (configurável)
- **Timeout de Requisição**: 30 segundos
- **Encoding**: UTF-8 para suporte completo ao português brasileiro

## Arquitetura do Sistema

O sistema utiliza uma arquitetura modular com classificadores especializados:

1. **Classificador Principal**: Determina a categoria geral da emergência
2. **Classificadores de Urgência**: Avaliam o nível de prioridade para cada serviço
3. **Sistema de Roteamento**: Direciona automaticamente para o serviço apropriado
4. **API REST**: Interface para integração com sistemas externos

## Benefícios

- **Redução do tempo de resposta**: Classificação automática elimina transferências desnecessárias
- **Melhoria na eficiência**: Recursos direcionados corretamente desde o primeiro contato
- **Padronização**: Processo consistente de triagem de emergências
- **Escalabilidade**: Sistema pode processar múltiplas chamadas simultaneamente

## Casos de Uso

- **Centrais de emergência**: Integração com sistemas 190, 192, 193
- **Hospitais**: Triagem automática de chamadas médicas
- **Corporações**: Sistema de emergência interno
- **Eventos**: Gestão de emergências em grandes eventos

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## Autor

**Djairo Filho**
- GitHub: [@djairofilho](https://github.com/djairofilho)
