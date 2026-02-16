"""
Utilitários para hashtags.
"""

import re


def extract_hashtags(text):
    """
    Extrai hashtags de um texto.
    
    Padrão: #palavra (letras, números, underscore)
    
    Exemplos:
    - "#python" → ["python"]
    - "#Django #API" → ["django", "api"]
    - "#Machine_Learning" → ["machine_learning"]
    - "Adorei #Python! #python" → ["python"] (sem duplicatas)
    
    Args:
        text (str): Texto para extrair hashtags
        
    Returns:
        list: Lista de hashtags (sem #, lowercase, sem duplicatas)
    """
    if not text:
        return []
    
    # Regex: # seguido de letras, números ou underscore
    # \w = [a-zA-Z0-9_]
    pattern = r'#(\w+)'
    hashtags = re.findall(pattern, text)
    
    # Normalizar: lowercase e remover duplicatas
    hashtags = list(set(tag.lower() for tag in hashtags))
    
    return sorted(hashtags)  # Ordenar para consistência