"""
Real-time Grammar Correction Service
Provides instant grammar, spelling, and style corrections
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import openai
from anthropic import Anthropic
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class CorrectionType(str, Enum):
    GRAMMAR = "grammar"
    SPELLING = "spelling"
    STYLE = "style"
    PUNCTUATION = "punctuation"
    VOCABULARY = "vocabulary"
    STRUCTURE = "structure"

@dataclass
class GrammarError:
    error_type: CorrectionType
    original_text: str
    corrected_text: str
    explanation: str
    confidence: float
    start_pos: int
    end_pos: int
    suggestion: str

class GrammarCorrectionRequest(BaseModel):
    text: str
    task_type: str = "Task 2"
    language: str = "en"
    correction_level: str = "comprehensive"  # basic, comprehensive, advanced

class GrammarCorrectionResponse(BaseModel):
    original_text: str
    corrected_text: str
    errors: List[Dict[str, Any]]
    suggestions: List[str]
    overall_score: float
    processing_time: float
    confidence: float

class RealTimeGrammarCorrector:
    """Advanced real-time grammar correction service"""
    
    def __init__(self, openai_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        self.openai_client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None
        self.anthropic_client = Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        self.is_available = bool(openai_api_key or anthropic_api_key)
        
        # Common grammar patterns
        self.grammar_patterns = {
            "subject_verb_disagreement": [
                r"\b(he|she|it)\s+(are|were)\b",
                r"\b(they|we|you)\s+(is|was)\b",
                r"\b(everyone|everybody|someone|somebody|anyone|anybody|no one|nobody)\s+(are|were)\b"
            ],
            "double_negatives": [
                r"\b(no|not|never|nothing|nobody|nowhere)\s+.*\s+(no|not|never|nothing|nobody|nowhere)\b"
            ],
            "incorrect_prepositions": [
                r"\b(in|on|at)\s+(the\s+)?(morning|afternoon|evening|night)\b",
                r"\b(depend|rely|focus)\s+(in|on)\b"
            ],
            "missing_articles": [
                r"\b(^|\s)(a|an|the)\s+(a|an|the)\b",  # Double articles
                r"\b(^|\s)([A-Z][a-z]+)\s+(is|are|was|were)\b"  # Missing article before noun
            ]
        }
        
        # IELTS-specific vocabulary improvements
        self.vocabulary_upgrades = {
            "good": ["excellent", "outstanding", "superior", "exceptional"],
            "bad": ["poor", "inadequate", "substandard", "deficient"],
            "big": ["significant", "substantial", "considerable", "extensive"],
            "small": ["minor", "minimal", "limited", "insignificant"],
            "important": ["crucial", "vital", "essential", "paramount"],
            "very": ["extremely", "highly", "remarkably", "exceptionally"],
            "many": ["numerous", "multiple", "various", "diverse"],
            "some": ["several", "various", "certain", "particular"]
        }
        
        if not self.is_available:
            logger.warning("⚠️ No LLM API keys provided, Grammar Corrector will use rule-based fallback")
    
    async def correct_text(self, request: GrammarCorrectionRequest) -> GrammarCorrectionResponse:
        """Correct grammar, spelling, and style in real-time"""
        
        if not self.is_available:
            return self._rule_based_correction(request)
        
        try:
            # Use AI for comprehensive correction
            ai_corrections = await self._ai_correction(request)
            
            # Combine with rule-based corrections
            rule_corrections = self._rule_based_correction(request)
            
            # Merge and prioritize corrections
            merged_result = self._merge_corrections(ai_corrections, rule_corrections)
            
            return merged_result
            
        except Exception as e:
            logger.error(f"❌ AI grammar correction failed: {e}")
            return self._rule_based_correction(request)
    
    async def _ai_correction(self, request: GrammarCorrectionRequest) -> GrammarCorrectionResponse:
        """Use AI for advanced grammar correction"""
        
        prompt = f"""
        You are an expert IELTS writing tutor. Please correct the following text for grammar, spelling, style, and IELTS-specific improvements.

        Task Type: {request.task_type}
        Correction Level: {request.correction_level}
        
        Text to correct:
        "{request.text}"
        
        Please provide:
        1. Corrected text
        2. List of errors found with explanations
        3. Overall writing quality score (1-9 IELTS band scale)
        4. Specific suggestions for improvement
        
        Format your response as JSON with the following structure:
        {{
            "corrected_text": "...",
            "errors": [
                {{
                    "type": "grammar|spelling|style|punctuation|vocabulary|structure",
                    "original": "...",
                    "corrected": "...",
                    "explanation": "...",
                    "confidence": 0.95,
                    "start_pos": 0,
                    "end_pos": 5,
                    "suggestion": "..."
                }}
            ],
            "suggestions": ["..."],
            "overall_score": 7.5,
            "confidence": 0.9
        }}
        """
        
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=2000
                )
                result_text = response.choices[0].message.content
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2000,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )
                result_text = response.content[0].text
            else:
                raise Exception("No AI client available")
            
            # Parse AI response
            import json
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                result = self._parse_ai_response_fallback(result_text, request.text)
            
            return GrammarCorrectionResponse(
                original_text=request.text,
                corrected_text=result.get("corrected_text", request.text),
                errors=result.get("errors", []),
                suggestions=result.get("suggestions", []),
                overall_score=result.get("overall_score", 6.0),
                processing_time=0.0,  # Will be set by caller
                confidence=result.get("confidence", 0.8)
            )
            
        except Exception as e:
            logger.error(f"❌ AI correction failed: {e}")
            raise e
    
    def _rule_based_correction(self, request: GrammarCorrectionRequest) -> GrammarCorrectionResponse:
        """Rule-based grammar correction fallback"""
        
        text = request.text
        errors = []
        suggestions = []
        
        # Check for common grammar errors
        for error_type, patterns in self.grammar_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    error_text = match.group(0)
                    corrected_text = self._correct_pattern(error_text, error_type)
                    
                    if corrected_text != error_text:
                        errors.append({
                            "type": "grammar",
                            "original": error_text,
                            "corrected": corrected_text,
                            "explanation": f"Corrected {error_type.replace('_', ' ')}",
                            "confidence": 0.8,
                            "start_pos": match.start(),
                            "end_pos": match.end(),
                            "suggestion": f"Consider: {corrected_text}"
                        })
        
        # Vocabulary improvements
        for basic_word, advanced_words in self.vocabulary_upgrades.items():
            if basic_word in text.lower():
                suggestions.append(f"Replace '{basic_word}' with more sophisticated vocabulary: {', '.join(advanced_words[:3])}")
        
        # Basic punctuation fixes
        corrected_text = self._fix_punctuation(text)
        
        # Calculate overall score
        error_count = len(errors)
        word_count = len(text.split())
        error_rate = error_count / max(word_count, 1)
        
        if error_rate < 0.05:  # Less than 5% errors
            overall_score = 8.0
        elif error_rate < 0.1:  # Less than 10% errors
            overall_score = 7.0
        elif error_rate < 0.15:  # Less than 15% errors
            overall_score = 6.0
        else:
            overall_score = 5.0
        
        return GrammarCorrectionResponse(
            original_text=request.text,
            corrected_text=corrected_text,
            errors=errors,
            suggestions=suggestions[:5],  # Limit suggestions
            overall_score=overall_score,
            processing_time=0.1,
            confidence=0.7
        )
    
    def _correct_pattern(self, text: str, error_type: str) -> str:
        """Correct specific grammar patterns"""
        
        corrections = {
            "subject_verb_disagreement": {
                "he are": "he is",
                "she are": "she is", 
                "it are": "it is",
                "they is": "they are",
                "we is": "we are",
                "you is": "you are",
                "everyone are": "everyone is",
                "everybody are": "everybody is"
            },
            "double_negatives": {
                "no nothing": "nothing",
                "not nothing": "nothing",
                "never no": "never any",
                "not never": "never"
            },
            "incorrect_prepositions": {
                "in the morning": "in the morning",  # This is correct
                "depend in": "depend on",
                "rely in": "rely on",
                "focus in": "focus on"
            }
        }
        
        if error_type in corrections:
            for wrong, right in corrections[error_type].items():
                if wrong.lower() in text.lower():
                    return text.replace(wrong, right)
        
        return text
    
    def _fix_punctuation(self, text: str) -> str:
        """Fix basic punctuation issues"""
        
        # Add spaces after periods if missing
        text = re.sub(r'\.([A-Z])', r'. \1', text)
        
        # Fix double spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Ensure proper capitalization
        sentences = text.split('. ')
        capitalized = []
        for sentence in sentences:
            if sentence.strip():
                capitalized.append(sentence.strip().capitalize())
        
        text = '. '.join(capitalized)
        
        # Ensure text ends with punctuation
        if text and not text[-1] in '.!?':
            text += '.'
        
        return text
    
    def _parse_ai_response_fallback(self, ai_response: str, original_text: str) -> Dict[str, Any]:
        """Fallback parser for AI responses that aren't valid JSON"""
        
        # Extract corrected text (look for text after "corrected_text:")
        corrected_match = re.search(r'corrected_text["\']?\s*:\s*["\']?([^"\']+)["\']?', ai_response, re.IGNORECASE)
        corrected_text = corrected_match.group(1) if corrected_match else original_text
        
        # Extract score
        score_match = re.search(r'score["\']?\s*:\s*(\d+\.?\d*)', ai_response, re.IGNORECASE)
        score = float(score_match.group(1)) if score_match else 6.0
        
        return {
            "corrected_text": corrected_text,
            "errors": [],
            "suggestions": ["AI correction completed"],
            "overall_score": score,
            "confidence": 0.7
        }
    
    def _merge_corrections(self, ai_result: GrammarCorrectionResponse, rule_result: GrammarCorrectionResponse) -> GrammarCorrectionResponse:
        """Merge AI and rule-based corrections"""
        
        # Use AI corrected text if available and confident
        if ai_result.confidence > 0.8:
            corrected_text = ai_result.corrected_text
        else:
            corrected_text = rule_result.corrected_text
        
        # Combine errors (remove duplicates)
        all_errors = ai_result.errors + rule_result.errors
        unique_errors = []
        seen_errors = set()
        
        for error in all_errors:
            error_key = f"{error['start_pos']}-{error['end_pos']}-{error['original']}"
            if error_key not in seen_errors:
                unique_errors.append(error)
                seen_errors.add(error_key)
        
        # Combine suggestions
        all_suggestions = list(set(ai_result.suggestions + rule_result.suggestions))
        
        # Use higher confidence score
        overall_score = ai_result.overall_score if ai_result.confidence > rule_result.confidence else rule_result.overall_score
        
        return GrammarCorrectionResponse(
            original_text=ai_result.original_text,
            corrected_text=corrected_text,
            errors=unique_errors,
            suggestions=all_suggestions[:10],  # Limit to 10 suggestions
            overall_score=overall_score,
            processing_time=ai_result.processing_time + rule_result.processing_time,
            confidence=max(ai_result.confidence, rule_result.confidence)
        )
    
    def get_correction_types(self) -> List[str]:
        """Get available correction types"""
        return [correction_type.value for correction_type in CorrectionType]
    
    def get_supported_languages(self) -> List[str]:
        """Get supported languages for correction"""
        return ["en", "es", "fr", "de", "it", "pt"]


