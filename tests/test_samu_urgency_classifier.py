#!/usr/bin/env python3
"""
Teste do classificador de urgência para chamadas de emergência médica (SAMU).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classifiers import classify_samu_urgency, generate_samu_instructions

def test_samu_urgency_classification():
    """Testa diferentes cenários de urgência para SAMU"""
    
    test_cases = [
        {
            "name": "CRÍTICA - Não respira + trauma alto risco",
            "transcript": "Um carro bateu em alta velocidade, o motorista não está respirando, tem muito sangue, preciso de ajuda urgente!"
        },
        {
            "name": "CRÍTICA - Inconsciente + sangramento intenso",
            "transcript": "Minha esposa desmaiou e não acorda, está sangrando muito do braço, não sei o que fazer!"
        },
        {
            "name": "ALTA - Convulsão + sangramento",
            "transcript": "Meu filho está tendo convulsão, bateu a cabeça e está sangrando, ele tem 8 anos!"
        },
        {
            "name": "ALTA - Inconsciente mas respira",
            "transcript": "Encontrei um homem desmaiado na rua, ele respira mas não acorda, não sei há quanto tempo está assim."
        },
        {
            "name": "MÉDIA - Dor no peito + idoso",
            "transcript": "Meu pai de 75 anos está com dor forte no peito, ele tem diabetes e pressão alta, está consciente."
        },
        {
            "name": "MÉDIA - Fratura exposta",
            "transcript": "Cai da escada e quebrei a perna, o osso está aparecendo, estou consciente mas com muita dor."
        },
        {
            "name": "BAIXA - Sintomas leves",
            "transcript": "Estou com dor de cabeça há algumas horas, não é muito forte mas queria saber se preciso ir ao hospital."
        },
        {
            "name": "CRÍTICA - Parto + complicações",
            "transcript": "Minha esposa está em trabalho de parto, o bebê está saindo mas ela está sangrando muito, socorro!"
        }
    ]
    
    print("🚑 TESTE DO CLASSIFICADOR DE URGÊNCIA PARA SAMU")
    print("=" * 60)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📞 TESTE {i}: {case['name']}")
        print(f"📝 Transcrição: {case['transcript']}")
        print("-" * 40)
        
        # Classifica a urgência para SAMU
        urgency_data = classify_samu_urgency(case['transcript'])
        
        print(f"🚨 Nível de Urgência: {urgency_data['urgency_level']}")
        print(f"📊 Confiança: {urgency_data['confidence']}%")
        print(f"💭 Motivo: {urgency_data['reasoning']}")
        
        # Mostra informações extraídas
        extracted_info = urgency_data.get('extracted_info', {})
        print(f"\n📋 Informações Extraídas:")
        print(f"   🩺 Sintoma principal: {extracted_info.get('main_symptom', 'N/A')}")
        print(f"   🫁 Consciência/respiração: {extracted_info.get('consciousness_breathing', 'N/A')}")
        print(f"   👤 Idade/condições: {extracted_info.get('age_conditions', 'N/A')}")
        print(f"   🩸 Sangramento/fratura: {extracted_info.get('bleeding_fracture', 'N/A')}")
        print(f"   🚗 Trauma alto risco: {extracted_info.get('high_risk_trauma', 'N/A')}")
        print(f"   🚪 Acesso/referência: {extracted_info.get('access_reference', 'N/A')}")
        
        # Gera instruções específicas para o SAMU
        samu_instructions = generate_samu_instructions(urgency_data)
        print(f"\n📋 Instruções para Despacho do SAMU:")
        print(samu_instructions)
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    test_samu_urgency_classification()
