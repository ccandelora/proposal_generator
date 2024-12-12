"""Text processing utilities."""
import re
from typing import List

def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text content
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
        
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove multiple line breaks
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Ensure proper spacing after punctuation
    text = re.sub(r'([.,!?])([^\s])', r'\1 \2', text)
    
    return text.strip()

def extract_sentences(text: str) -> List[str]:
    """
    Extract sentences from text.
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    if not text:
        return []
        
    # Clean text first
    text = clean_text(text)
    
    # Split on sentence endings while preserving the punctuation
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Clean and filter sentences
    sentences = [
        s.strip() 
        for s in sentences 
        if s.strip() and len(s.split()) > 3  # Only keep sentences with >3 words
    ]
    
    return sentences

def extract_keywords(text: str, min_length: int = 4) -> List[str]:
    """
    Extract potential keywords from text.
    
    Args:
        text: Input text
        min_length: Minimum word length to consider
        
    Returns:
        List of potential keywords
    """
    if not text:
        return []
        
    # Clean text
    text = clean_text(text)
    
    # Split into words and filter
    words = text.lower().split()
    words = [
        word for word in words
        if len(word) >= min_length and word.isalnum()
    ]
    
    # Remove duplicates while preserving order
    seen = set()
    keywords = []
    for word in words:
        if word not in seen:
            keywords.append(word)
            seen.add(word)
    
    return keywords

def calculate_readability(text: str) -> float:
    """
    Calculate readability score (0-1).
    
    Args:
        text: Input text
        
    Returns:
        Readability score between 0 and 1
    """
    if not text:
        return 0.0
        
    try:
        sentences = extract_sentences(text)
        if not sentences:
            return 0.0
            
        # Calculate average sentence length
        words_per_sentence = [len(s.split()) for s in sentences]
        avg_sentence_length = sum(words_per_sentence) / len(words_per_sentence)
        
        # Penalize very short or very long sentences
        # Optimal range is 10-20 words
        if avg_sentence_length < 5:
            return 0.3
        elif avg_sentence_length > 30:
            return 0.4
        elif 10 <= avg_sentence_length <= 20:
            return 1.0
        else:
            # Linear falloff outside optimal range
            return max(0.5, 1.0 - abs(avg_sentence_length - 15) / 30)
            
    except Exception:
        return 0.0 