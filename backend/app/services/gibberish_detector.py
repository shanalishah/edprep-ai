"""
Gibberish Detection System for IELTS Writing Assessment
Detects meaningless text and prevents false high scores
"""

import re
import string
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class GibberishDetector:
    """Advanced gibberish detection for IELTS essays"""
    
    def __init__(self):
        # Common English words (most frequent 1000 words)
        self.common_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
            'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just',
            'him', 'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then',
            'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first',
            'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us', 'is', 'was', 'are', 'been',
            'has', 'had', 'were', 'said', 'each', 'which', 'their', 'said', 'will', 'about', 'if', 'up', 'out', 'many', 'then', 'them',
            'can', 'only', 'other', 'new', 'some', 'these', 'may', 'say', 'each', 'which', 'she', 'do', 'how', 'its', 'now', 'find',
            'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part', 'over', 'such', 'much', 'through', 'very', 'when',
            'here', 'just', 'where', 'most', 'know', 'little', 'before', 'great', 'should', 'because', 'each', 'which', 'she', 'do',
            'how', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part', 'over', 'such', 'much'
        }
        
        # Patterns that indicate gibberish
        self.gibberish_patterns = [
            r'^[a-z\s]{1,50}$',  # All lowercase, short
            r'[qwertyuiop]{4,}',  # Keyboard mashing (4+ chars)
            r'[asdfghjkl]{4,}',   # Keyboard mashing (4+ chars)
            r'[zxcvbnm]{4,}',     # Keyboard mashing (4+ chars)
            r'[1234567890]{4,}',  # Number sequences (4+ chars)
            r'[!@#$%^&*()]{4,}',  # Symbol sequences (4+ chars)
            r'(.)\1{5,}',         # Repeated characters (6+ times)
        ]
    
    def detect_gibberish(self, text: str) -> Dict[str, Any]:
        """Detect if text is gibberish and return analysis"""
        
        if not text or not text.strip():
            return {
                'is_gibberish': True,
                'confidence': 1.0,
                'reasons': ['Empty or whitespace only'],
                'meaningful_ratio': 0.0,
                'word_count': 0,
                'meaningful_words': 0,
                'score': 1.0
            }
        
        text = text.strip().lower()
        words = text.split()
        
        # Check for very short text (only flag if it's clearly gibberish)
        if len(text) < 10:
            return {
                'is_gibberish': True,
                'confidence': 0.9,
                'reasons': ['Text too short (less than 10 characters)'],
                'meaningful_ratio': 0.0,
                'word_count': len(words),
                'meaningful_words': 0,
                'score': 1.0
            }
        
        # Check word count (only flag if it's clearly gibberish)
        if len(words) < 3:
            return {
                'is_gibberish': True,
                'confidence': 0.9,
                'reasons': ['Too few words (less than 3 words)'],
                'meaningful_ratio': 0.0,
                'word_count': len(words),
                'meaningful_words': 0,
                'score': 1.0
            }
        
        # Check for keyboard mashing patterns
        gibberish_reasons = []
        confidence = 0.0
        
        # Pattern matching
        for pattern in self.gibberish_patterns:
            if re.search(pattern, text):
                gibberish_reasons.append(f'Matches gibberish pattern: {pattern}')
                confidence += 0.2
        
        # Check for meaningful words
        meaningful_words = 0
        total_words = len(words)
        
        for word in words:
            # Clean word of punctuation
            clean_word = word.strip(string.punctuation)
            if clean_word in self.common_words:
                meaningful_words += 1
        
        # Calculate meaningful word ratio
        meaningful_ratio = meaningful_words / total_words if total_words > 0 else 0
        
        # If less than 20% meaningful words, likely gibberish
        if meaningful_ratio < 0.2:
            gibberish_reasons.append(f'Low meaningful word ratio: {meaningful_ratio:.2f}')
            confidence += 0.4
        
        # Check for sentence structure
        sentences = re.split(r'[.!?]+', text)
        valid_sentences = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence.split()) >= 3:  # At least 3 words per sentence
                valid_sentences += 1
        
        if valid_sentences == 0:
            gibberish_reasons.append('No valid sentence structure')
            confidence += 0.3
        
        # Check for repeated words/phrases
        word_counts = {}
        for word in words:
            clean_word = word.strip(string.punctuation)
            if len(clean_word) > 2:  # Only count words longer than 2 chars
                word_counts[clean_word] = word_counts.get(clean_word, 0) + 1
        
        # If any word appears more than 30% of the time, likely gibberish
        for word, count in word_counts.items():
            if count / total_words > 0.3:
                gibberish_reasons.append(f'Excessive repetition of "{word}"')
                confidence += 0.2
        
        # Determine if gibberish
        is_gibberish = confidence > 0.7 or len(gibberish_reasons) >= 3
        
        # Calculate appropriate score
        if is_gibberish:
            score = 1.0
        elif meaningful_ratio < 0.5:
            score = 2.0
        elif meaningful_ratio < 0.7:
            score = 3.0
        else:
            score = None  # Let normal scoring handle it
        
        return {
            'is_gibberish': is_gibberish,
            'confidence': min(confidence, 1.0),
            'reasons': gibberish_reasons,
            'meaningful_ratio': meaningful_ratio,
            'word_count': total_words,
            'meaningful_words': meaningful_words,
            'score': score
        }
    
    def get_gibberish_feedback(self, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appropriate feedback for gibberish detection"""
        
        if not detection_result['is_gibberish']:
            return None
        
        reasons = detection_result['reasons']
        
        detailed_feedback = f"""
This text appears to be gibberish or meaningless content. 

**Detection Results:**
- Meaningful word ratio: {detection_result['meaningful_ratio']:.2f}
- Word count: {detection_result['word_count']}
- Detection confidence: {detection_result['confidence']:.2f}

**Issues identified:**
{chr(10).join(f"• {reason}" for reason in reasons)}

**Band Score: 1.0** - This is not a valid IELTS essay response.
"""
        
        return {
            'detailed_feedback': detailed_feedback.strip(),
            'suggestions': [
                'Please write a proper essay response to the task',
                'Use meaningful English words and sentences',
                'Address the essay prompt directly',
                'Include relevant examples and arguments',
                'Follow proper essay structure'
            ],
            'improvement_plan': {
                'immediate_focus': ['Write a proper essay response'],
                'short_term_goals': ['Learn basic essay writing skills'],
                'long_term_goals': ['Develop IELTS writing proficiency'],
                'recommended_resources': ['IELTS writing guides', 'Basic English writing courses']
            },
            'strengths_weaknesses': {
                'strengths': [],
                'weaknesses': ['Not a valid essay response', 'Meaningless content', 'No task achievement']
            },
            'error_analysis': reasons,
            'feedback_type': 'gibberish_detection'
        }
