#!/usr/bin/env python3
"""
Script de teste para validar a implementação do caso "policia-analogia".
Testa a detecção de chamadas disfarçadas e classificação normal.
"""

from classifier import classify_emergency_call, detect_disguised_call

def test_disguised_calls():
    """Testa chamadas disfarçadas que devem ser detectadas"""
    print("=== TESTANDO CHAMADAS DISFARÇADAS ===")
    
    test_cases = [
        "Olá, gostaria de pedir uma pizza de espinafre com ketchup",
        "Vocês fazem pizza de espinafre com ketchup?",
        "Quero uma pizza de espinafre e ketchup por favor",
        "Tem pizza de espinafre com ketchup no cardápio?",
    ]
    
    for i, transcript in enumerate(test_cases, 1):
        print(f"\nTeste {i}: {transcript}")
        result = classify_emergency_call(transcript)
        print(f"  Categoria: {result['category']}")
        print(f"  Confiança: {result['confidence']}%")
        print(f"  Motivo: {result['reasoning']}")
        
        # Verifica se foi detectada corretamente
        if result['category'] == 'policia-analogia':
            print("  ✅ CORRETO: Chamada disfarçada detectada")
        else:
            print("  ❌ ERRO: Chamada disfarçada NÃO detectada")

def test_normal_calls():
    """Testa chamadas normais que NÃO devem ser detectadas como disfarçadas"""
    print("\n=== TESTANDO CHAMADAS NORMAIS ===")
    
    test_cases = [
        ("Preciso da polícia, fui assaltado", "policia"),
        ("Tem uma briga na rua, preciso de ajuda", "policia"),
        ("Quero pedir uma pizza de calabresa", "trote"),
        ("Gostaria de uma pizza de margherita", "trote"),
        ("Tem pizza de frango com catupiry?", "trote"),
    ]
    
    for i, (transcript, expected_category) in enumerate(test_cases, 1):
        print(f"\nTeste {i}: {transcript}")
        result = classify_emergency_call(transcript)
        print(f"  Categoria: {result['category']}")
        print(f"  Confiança: {result['confidence']}%")
        print(f"  Motivo: {result['reasoning']}")
        
        # Verifica se foi classificada corretamente
        if result['category'] == expected_category:
            print(f"  ✅ CORRETO: Classificada como {expected_category}")
        else:
            print(f"  ❌ ERRO: Esperado {expected_category}, mas foi {result['category']}")

def test_detection_function():
    """Testa a função de detecção diretamente"""
    print("\n=== TESTANDO FUNÇÃO DE DETECÇÃO DIRETA ===")
    
    test_cases = [
        ("pizza de espinafre com ketchup", True),
        ("quero uma pizza de espinafre e ketchup", True),
        ("pizza de calabresa", False),
        ("pizza de margherita", False),
        ("espinafre ketchup pizza", True),
    ]
    
    for transcript, expected in test_cases:
        result = detect_disguised_call(transcript)
        detected = result['is_disguised']
        print(f"Texto: '{transcript}'")
        print(f"Esperado: {expected}, Detectado: {detected}")
        
        if detected == expected:
            print("  ✅ CORRETO")
        else:
            print("  ❌ ERRO")
        print()

if __name__ == "__main__":
    print("🧪 INICIANDO TESTES DO SISTEMA POLICIA-ANALOGIA")
    print("=" * 60)
    
    test_detection_function()
    test_disguised_calls()
    test_normal_calls()
    
    print("\n" + "=" * 60)
    print("✅ TESTES CONCLUÍDOS")
