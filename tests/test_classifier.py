"""
Script de teste do classificador de chamadas de emergência.
Testa com dados mockados antes de integrar com chamadas reais.
"""

from classifiers import classify_emergency_call

# Dados mockados para teste
test_cases = [
    {
        "name": "Roubo",
        "text": "Alguém me roubou na rua, levaram minha bolsa. Preciso de ajuda da polícia urgente!"
    },
    {
        "name": "Acidente com feridos",
        "text": "Bateu um carro na esquina da minha rua, tem pessoas machucadas precisando de socorro médico"
    },
    {
        "name": "Incêndio",
        "text": "Tem um prédio pegando fogo na avenida principal, está saindo muita fumaça. Precisam dos bombeiros!"
    },
    {
        "name": "Infarto",
        "text": "Meu pai está com dor no peito e falta de ar, acho que está tendo um infarto. Enviem uma ambulância"
    },
    {
        "name": "Vazamento de gás",
        "text": "Está cheirando muito gás no meu prédio, pode explodir a qualquer momento. Venham rápido!"
    },
    {
        "name": "Trote",
        "text": "Hahaha, só ligando aqui pra zoar mesmo. Deixa eu falar com o patrão aí"
    },
    {
        "name": "Briga na rua",
        "text": "Tem uma briga violenta acontecendo aqui na rua, dois caras se agredindo. Precisam da polícia urgente"
    },
    {
        "name": "Afogamento",
        "text": "Pessoa se afogando na praia, já chamaram os bombeiros mas não chegaram ainda"
    },
    {
        "name": "Trote 2",
        "text": "Ae galera, vou testar esse sistema aqui rapidinho pra ver se funciona"
    },
    {
        "name": "Indefinido",
        "text": "Olá, bom dia. Eu estava pensando e queria tirar uma dúvida sobre algo"
    }
]

def test_classifier():
    """Roda todos os testes mockados"""
    print("=" * 80)
    print("TESTE DO CLASSIFICADOR DE CHAMADAS DE EMERGÊNCIA")
    print("=" * 80)
    print()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTeste {i}: {test_case['name']}")
        print(f"Texto: \"{test_case['text']}\"")
        print("-" * 80)
        
        result = classify_emergency_call(test_case['text'])
        
        print(f"✓ Categoria: {result['category'].upper()}")
        print(f"✓ Confiança: {result['confidence']}%")
        print(f"✓ Motivo: {result['reasoning']}")
        print()
    
    print("=" * 80)
    print("Todos os testes concluídos!")
    print("=" * 80)

if __name__ == "__main__":
    test_classifier()
