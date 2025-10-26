#!/usr/bin/env python3
"""
Teste do classificador de urgência para chamadas de emergência policial.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classifiers import classify_police_urgency, generate_police_instructions

def test_police_urgency_classification():
    """Testa diferentes cenários de urgência POLICIAL"""
    
    test_cases = [
        {
            "name": "CRÍTICA - Arma de fogo + autor presente + vítimas",
            "transcript": "Tem um homem armado aqui na minha casa, ele ainda está aqui, minha esposa está sangrando muito, preciso de ajuda urgente!"
        },
        {
            "name": "ALTA - Arma de fogo + autor fugiu",
            "transcript": "Um homem com revólver assaltou a loja e fugiu de carro prata, placa ABC-1234, direção centro. Não há feridos."
        },
        {
            "name": "MÉDIA - Crime em andamento sem arma",
            "transcript": "Tem uma briga aqui na rua, dois homens se agredindo, não vejo arma, mas está violento."
        },
        {
            "name": "BAIXA - Crime já ocorreu",
            "transcript": "Minha casa foi roubada ontem à noite, o ladrão já fugiu, não há ninguém aqui agora."
        },
        {
            "name": "CRÍTICA - Chamada disfarçada (pizza)",
            "transcript": "Oi, quero pedir uma pizza de espinafre com ketchup, é urgente, tem alguém aqui que precisa muito."
        }
    ]
    
    print("🚨 TESTE DO CLASSIFICADOR DE URGÊNCIA POLICIAL")
    print("=" * 60)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📞 TESTE {i}: {case['name']}")
        print(f"📝 Transcrição: {case['transcript']}")
        print("-" * 40)
        
        # Classifica a urgência POLICIAL
        urgency_data = classify_police_urgency(case['transcript'])
        
        print(f"🚨 Nível de Urgência: {urgency_data['urgency_level']}")
        print(f"📊 Confiança: {urgency_data['confidence']}%")
        print(f"💭 Motivo: {urgency_data['reasoning']}")
        
        # Mostra informações extraídas
        extracted_info = urgency_data.get('extracted_info', {})
        print(f"\n📋 Informações Extraídas:")
        print(f"   👤 Autor presente: {extracted_info.get('author_present', 'N/A')}")
        print(f"   🔫 Armas envolvidas: {extracted_info.get('weapons_involved', 'N/A')}")
        print(f"   ⏰ Timing do crime: {extracted_info.get('crime_timing', 'N/A')}")
        print(f"   🏥 Vítimas feridas: {extracted_info.get('victims_injured', 'N/A')}")
        print(f"   🏠 Local seguro: {extracted_info.get('location_safe', 'N/A')}")
        
        # Gera instruções específicas para a polícia
        police_instructions = generate_police_instructions(urgency_data)
        print(f"\n📋 Instruções para Despacho POLICIAL:")
        print(police_instructions)
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    test_police_urgency_classification()
