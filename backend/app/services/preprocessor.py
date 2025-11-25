import re
from typing import List

# Simple stopwords lists
STOPWORDS_EN = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been', 'be',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
}

STOPWORDS_ID = {
    'yang', 'dan', 'di', 'dari', 'untuk', 'pada', 'dengan', 'ini', 'itu',
    'adalah', 'akan', 'telah', 'atau', 'juga', 'serta', 'oleh', 'ke', 'dalam'
}

def preprocess_text(text: str, min_word_length: int = 3) -> str:
    """
    Clean dan preprocess text untuk topic modeling
    
    Args:
        text: Input text
        min_word_length: Minimum panjang kata
    """
    if not text:
        return ""
    
    # Lowercase
    text = text.lower()
    
    # Remove special characters, keep only alphanumeric and spaces
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    
    # Remove extra spaces
    text = ' '.join(text.split())
    
    # Remove stopwords and short words
    words = text.split()
    words = [
        w for w in words 
        if len(w) >= min_word_length 
        and w not in STOPWORDS_EN 
        and w not in STOPWORDS_ID
    ]
    
    return ' '.join(words)

def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """Extract top keywords dari text menggunakan simple frequency"""
    from collections import Counter
    
    cleaned = preprocess_text(text)
    words = cleaned.split()
    
    # Count frequencies
    word_freq = Counter(words)
    
    # Return top N
    return [word for word, _ in word_freq.most_common(top_n)]