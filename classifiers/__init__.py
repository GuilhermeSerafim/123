# Pasta de classificadores para o sistema de classificação de emergências

from .classifier import classify_emergency_call, detect_disguised_call
from .police_urgency_classifier import classify_police_urgency, generate_police_instructions
from .firefighter_urgency_classifier import classify_firefighter_urgency, generate_firefighter_instructions
from .samu_urgency_classifier import classify_samu_urgency, generate_samu_instructions

__all__ = [
    'classify_emergency_call',
    'detect_disguised_call', 
    'classify_police_urgency',
    'generate_police_instructions',
    'classify_firefighter_urgency',
    'generate_firefighter_instructions',
    'classify_samu_urgency',
    'generate_samu_instructions'
]
