# 🧠 Classificadores do Sistema de Emergências

Esta pasta contém todos os classificadores do sistema de classificação de emergências.

## 📁 Estrutura dos Classificadores

```
classifiers/
├── __init__.py                           # Torna a pasta um pacote Python
├── classifier.py                         # 🧠 Classificador geral de emergências
├── urgency_classifier.py                 # 🚨 Classificador de urgência POLICIAL
├── firefighter_urgency_classifier.py     # 🚒 Classificador de urgência de BOMBEIROS
└── README.md                            # Esta documentação
```

## 🧠 Tipos de Classificadores

### 1. **Classificador Geral** (`classifier.py`)
- **Função**: `classify_emergency_call(transcript)`
- **Categorias**: policia, samu, bombeiros, trote, indefinido, policia-analogia
- **Detecção**: Chamadas disfarçadas (pizza de espinafre com ketchup)
- **Uso**: Primeira classificação para determinar o tipo de emergência

### 2. **Classificador de Urgência POLICIAL** (`urgency_classifier.py`)
- **Função**: `classify_police_urgency(transcript)`
- **Níveis**: CRÍTICA, ALTA, MÉDIA, BAIXA
- **Critérios**: P1-P6 (autor presente, armas, vítimas, etc.)
- **Uso**: Ativado automaticamente quando categoria = "policia"

### 3. **Classificador de Urgência de BOMBEIROS** (`firefighter_urgency_classifier.py`)
- **Função**: `classify_firefighter_urgency(transcript)`
- **Níveis**: CRÍTICA, ALTA, MÉDIA, BAIXA
- **Critérios**: P1-P6 (tipo de emergência, pessoas presas, materiais perigosos, etc.)
- **Uso**: Ativado automaticamente quando categoria = "bombeiros"

## 🔧 Como Usar

### Importação Simples
```python
from classifiers import (
    classify_emergency_call,
    classify_police_urgency,
    generate_police_instructions,
    classify_firefighter_urgency,
    generate_firefighter_instructions
)
```

### Exemplo de Uso
```python
# 1. Classificação geral
classification = classify_emergency_call("Tem um incêndio na minha casa!")
print(classification['category'])  # "bombeiros"

# 2. Se for bombeiros, classifica urgência
if classification['category'] == 'bombeiros':
    urgency = classify_firefighter_urgency("Tem um incêndio na minha casa!")
    instructions = generate_firefighter_instructions(urgency)
    print(instructions)
```

## 📊 Fluxo de Classificação

```
Chamada Recebida
       ↓
Classificador Geral (classifier.py)
       ↓
   Categoria?
   ├── policia → Classificador de Urgência POLICIAL
   ├── bombeiros → Classificador de Urgência de BOMBEIROS
   ├── samu → (sem classificador específico ainda)
   └── outros → (sem classificador específico ainda)
       ↓
   Instruções Específicas
```

## 🎯 Objetivos dos Classificadores

### Polícia
- **Objetivo**: Proteger vidas, cessar crime, preservar local
- **Critérios**: Autor presente, armas envolvidas, vítimas feridas, etc.

### Bombeiros
- **Objetivo**: Eliminar risco de fogo, explosão, colapso ou aprisionamento
- **Critérios**: Tipo de emergência, pessoas presas, materiais perigosos, etc.

## 🔄 Extensibilidade

Para adicionar novos classificadores:

1. Crie um novo arquivo na pasta `classifiers/`
2. Implemente as funções de classificação
3. Adicione as importações no `__init__.py`
4. Integre no `app.py` se necessário
5. Crie testes na pasta `tests/`

## 📝 Padrão de Nomenclatura

- **Arquivos**: `nome_classifier.py`
- **Funções principais**: `classify_nome_urgency(transcript)`
- **Funções de instrução**: `generate_nome_instructions(urgency_data)`
- **Retorno**: Dict com `urgency_level`, `confidence`, `reasoning`, `extracted_info`
