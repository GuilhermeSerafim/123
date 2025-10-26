#!/usr/bin/env python3
"""
Teste do classificador de urgência para chamadas de emergência de bombeiros.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classifiers import classify_firefighter_urgency, generate_firefighter_instructions

def test_firefighter_urgency_classification():
    """Testa diferentes cenários de urgência para BOMBEIROS"""
    
    test_cases = [
        {
            "name": "CRÍTICA - Pessoas presas + chamas altas + botijão de gás",
            "transcript": "Tem um incêndio na casa ao lado, tem gente presa dentro, as chamas estão altas e tem botijão de gás lá! Socorro!"
        },
        {
            "name": "ALTA - Pessoas presas + chamas altas",
            "transcript": "Um carro pegou fogo na estrada, tem pessoas presas dentro, as chamas estão muito altas, preciso de ajuda urgente!"
        },
        {
            "name": "ALTA - Chamas altas + materiais perigosos",
            "transcript": "A fábrica está pegando fogo, tem produtos químicos lá dentro, as chamas estão altas e a fumaça está preta!"
        },
        {
            "name": "MÉDIA - Chamas visíveis sem pessoas presas",
            "transcript": "Tem um incêndio no poste da rua, vejo chamas, mas não tem ninguém preso, só precisa apagar o fogo."
        },
        {
            "name": "MÉDIA - Muita fumaça + vazamento de gás",
            "transcript": "Tem muito cheiro de gás na rua e muita fumaça saindo de uma casa, não vejo chamas mas o cheiro está forte."
        },
        {
            "name": "BAIXA - Apenas cheiro de queimado",
            "transcript": "Tem um cheiro de queimado na rua, não vejo fogo nem fumaça, mas o cheiro está incomodando."
        },
        {
            "name": "CRÍTICA - Queda de árvore com pessoas presas",
            "transcript": "Uma árvore caiu em cima de um carro, tem gente presa dentro, e tem fios elétricos soltos! Socorro!"
        }
    ]
    
    print("🚒 TESTE DO CLASSIFICADOR DE URGÊNCIA PARA BOMBEIROS")
    print("=" * 60)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📞 TESTE {i}: {case['name']}")
        print(f"📝 Transcrição: {case['transcript']}")
        print("-" * 40)
        
        # Classifica a urgência para BOMBEIROS
        urgency_data = classify_firefighter_urgency(case['transcript'])
        
        print(f"🚨 Nível de Urgência: {urgency_data['urgency_level']}")
        print(f"📊 Confiança: {urgency_data['confidence']}%")
        print(f"💭 Motivo: {urgency_data['reasoning']}")
        
        # Mostra informações extraídas
        extracted_info = urgency_data.get('extracted_info', {})
        print(f"\n📋 Informações Extraídas:")
        print(f"   🔥 Tipo de emergência: {extracted_info.get('emergency_type', 'N/A')}")
        print(f"   👥 Pessoas presas: {extracted_info.get('people_trapped', 'N/A')}")
        print(f"   🔥 Visibilidade do fogo: {extracted_info.get('fire_visibility', 'N/A')}")
        print(f"   ⚠️ Materiais perigosos: {extracted_info.get('dangerous_materials', 'N/A')}")
        print(f"   🚗 Rota de acesso: {extracted_info.get('access_route', 'N/A')}")
        print(f"   🧯 Tentativa de combate: {extracted_info.get('combat_attempt', 'N/A')}")
        
        # Gera instruções específicas para os bombeiros
        firefighter_instructions = generate_firefighter_instructions(urgency_data)
        print(f"\n📋 Instruções para Despacho de BOMBEIROS:")
        print(firefighter_instructions)
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    test_firefighter_urgency_classification()
