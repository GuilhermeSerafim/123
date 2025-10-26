#!/usr/bin/env python3
"""
Executa todos os testes do sistema de classificação de emergências.
"""

import sys
import os

# Adiciona o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_all_tests():
    """Executa todos os testes disponíveis"""
    
    print("🧪 EXECUTANDO TODOS OS TESTES DO SISTEMA")
    print("=" * 60)
    
    # Teste 1: Classificador de urgência policial
    print("\n🚨 TESTE 1: Classificador de Urgência POLICIAL")
    print("-" * 50)
    try:
        from test_urgency_classifier import test_police_urgency_classification
        test_police_urgency_classification()
        print("✅ Teste de urgência policial: PASSOU")
    except Exception as e:
        print(f"❌ Teste de urgência policial: FALHOU - {e}")
    
    # Teste 2: Classificador geral (se existir)
    print("\n🎯 TESTE 2: Classificador Geral")
    print("-" * 50)
    try:
        from test_classifier import test_classification
        test_classification()
        print("✅ Teste de classificação geral: PASSOU")
    except Exception as e:
        print(f"❌ Teste de classificação geral: FALHOU - {e}")
    
    # Teste 3: Polícia analogia (se existir)
    print("\n🍕 TESTE 3: Polícia Analogia")
    print("-" * 50)
    try:
        from test_policia_analogia import test_policia_analogia
        test_policia_analogia()
        print("✅ Teste de polícia analogia: PASSOU")
    except Exception as e:
        print(f"❌ Teste de polícia analogia: FALHOU - {e}")
    
    print("\n" + "=" * 60)
    print("🏁 TODOS OS TESTES CONCLUÍDOS")

if __name__ == "__main__":
    run_all_tests()
