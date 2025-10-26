# 🧪 Testes do Sistema de Classificação de Emergências

Esta pasta contém todos os testes do sistema de classificação de emergências.

## 📁 Estrutura dos Testes

```
tests/
├── __init__.py                           # Torna a pasta um pacote Python
├── run_all_tests.py                     # Executa todos os testes
├── test_police_urgency_classifier.py    # Testes do classificador de urgência POLICIAL
├── test_firefighter_urgency_classifier.py  # Testes do classificador de urgência de BOMBEIROS
├── test_classifier.py                   # Testes do classificador geral
├── test_policia_analogia.py             # Testes de chamadas disfarçadas
└── README.md                            # Esta documentação
```

## 🚀 Como Executar

### Executar Todos os Testes
```bash
cd Classificador
python tests/run_all_tests.py
```

### Executar Teste Específico
```bash
# Teste de urgência policial
python tests/test_police_urgency_classifier.py

# Teste de classificação geral
python tests/test_classifier.py

# Teste de urgência de bombeiros
python tests/test_firefighter_urgency_classifier.py

# Teste de polícia analogia
python tests/test_policia_analogia.py
```

## 🧪 Tipos de Testes

### 1. **Teste de Urgência POLICIAL** (`test_police_urgency_classifier.py`)
- Testa 5 cenários diferentes de urgência
- Valida níveis: CRÍTICA, ALTA, MÉDIA, BAIXA
- Verifica extração de informações (P1-P6)
- Gera instruções para despacho policial

### 2. **Teste de Classificação Geral** (`test_classifier.py`)
- Testa classificação em categorias: policia, samu, bombeiros, trote, indefinido
- Valida detecção de chamadas disfarçadas
- Testa diferentes tipos de emergências

### 3. **Teste de Urgência de BOMBEIROS** (`test_firefighter_urgency_classifier.py`)
- Testa 7 cenários diferentes de urgência para bombeiros
- Valida níveis: CRÍTICA, ALTA, MÉDIA, BAIXA
- Verifica extração de informações (P1-P6) específicas para bombeiros
- Gera instruções para despacho de bombeiros

### 4. **Teste de Polícia Analogia** (`test_policia_analogia.py`)
- Testa detecção de chamadas disfarçadas
- Valida padrões como "pizza de espinafre com ketchup"
- Verifica classificação como "policia-analogia"

## 📊 Exemplo de Saída

```
🧪 EXECUTANDO TODOS OS TESTES DO SISTEMA
============================================================

🚨 TESTE 1: Classificador de Urgência POLICIAL
--------------------------------------------------
🚨 TESTE DO CLASSIFICADOR DE URGÊNCIA POLICIAL
============================================================

📞 TESTE 1: CRÍTICA - Arma de fogo + autor presente + vítimas
📝 Transcrição: Tem um homem armado aqui na minha casa...
🚨 Nível de Urgência: CRÍTICA
📊 Confiança: 95%
💭 Motivo: Arma de fogo presente + autor no local + vítimas feridas

✅ Teste de urgência policial: PASSOU

🎯 TESTE 2: Classificador Geral
--------------------------------------------------
✅ Teste de classificação geral: PASSOU

🍕 TESTE 3: Polícia Analogia
--------------------------------------------------
✅ Teste de polícia analogia: PASSOU

============================================================
🏁 TODOS OS TESTES CONCLUÍDOS
```

## 🔧 Configuração

Os testes são executados a partir da pasta `Classificador` e importam automaticamente os módulos necessários. Não é necessário configuração adicional.

## 📝 Adicionando Novos Testes

Para adicionar novos testes:

1. Crie um arquivo `test_nome_do_teste.py`
2. Importe os módulos necessários usando o padrão:
   ```python
   import sys
   import os
   sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
   ```
3. Adicione o teste ao `run_all_tests.py` se necessário
4. Documente o teste neste README
