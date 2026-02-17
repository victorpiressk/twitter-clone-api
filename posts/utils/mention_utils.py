"""
Utilitários para menções.
"""

import re


def extract_mentions(text):
    """
    Extrai menções (@username) de um texto.
    
    Exemplos:
    - "Olá @alice" → ["alice"]
    - "@bob e @charlie" → ["bob", "charlie"]
    - "Olá @Alice @alice" → ["alice"] (sem duplicatas)
    
    Args:
        text (str): Texto para extrair menções
        
    Returns:
        list: Lista de usernames mencionados (sem @, lowercase, sem duplicatas)
    """
    if not text:
        return []
    
    # Regex: @ seguido de letras, números ou underscore
    # \w = [a-zA-Z0-9_]
    pattern = r'@(\w+)'
    mentions = re.findall(pattern, text)
    
    # Normalizar: lowercase e remover duplicatas
    mentions = list(set(m.lower() for m in mentions))
    
    return sorted(mentions)  # Ordenar para consistência
