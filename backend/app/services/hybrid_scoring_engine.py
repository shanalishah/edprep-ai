"""
Hybrid Scoring Engine
Combines LLM analysis with rule-based scoring for optimal results
"""

import logging
from typing import Dict, Any, Optional
from .ml_scoring_engine import AdvancedMLScoringEngine
from .llm_scoring_engine import LLMScoringEngine

logger = logging.getLogger(__name__)

class HybridScoringEngine:
    """Hybrid scoring engine combining LLM and rule-based approaches"""
    
    def __init__(self, models_dir: str, openai_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        self.rule_engine = AdvancedMLScoringEngine(models_dir)
        self.llm_engine = LLMScoringEngine(openai_api_key, anthropic_api_key)
        self.llm_available = self.llm_engine.is_available
        
        if self.llm_available:
            logger.info("✅ Hybrid scoring engine initialized with LLM support")
        else:
            logger.info("⚠️ Hybrid scoring engine initialized with rule-based only")
    
    def score_essay(self, prompt: str, essay: str, task_type: str) -> Dict[str, Any]:
        """Score essay using hybrid approach"""
        
        # Get rule-based scores
        rule_result = self.rule_engine.score_essay(prompt, essay, task_type)
        
        if not self.llm_available:
            logger.info("🔄 LLM not available, using rule-based scoring only")
            return rule_result
        
        try:
            # Get LLM scores
            llm_result = self.llm_engine.score_essay_with_llm(prompt, essay, task_type)
            
            # Combine scores with weighted approach
            combined_scores = self._combine_scores(
                rule_result["scores"], 
                llm_result["scores"],
                weights={"rule": 0.3, "llm": 0.7}  # Favor LLM for better understanding
            )
            
            # Use LLM feedback if available
            feedback = llm_result.get("feedback", rule_result.get("feedback", {}))
            
            # Calculate combined confidence
            confidence = self._calculate_combined_confidence(
                rule_result.get("confidence", 0.8),
                llm_result.get("confidence", 0.9)
            )
            
            return {
                "scores": combined_scores,
                "feedback": feedback,
                "error_analysis": rule_result.get("error_analysis", {}),
                "is_gibberish": rule_result.get("is_gibberish", False),
                "confidence": confidence,
                "assessment_method": "hybrid_llm_rule",
                "component_scores": {
                    "rule_based": rule_result["scores"],
                    "llm_based": llm_result["scores"]
                },
                "reasoning": llm_result.get("reasoning", "Combined rule-based and LLM analysis")
            }
            
        except Exception as e:
            logger.warning(f"⚠️ LLM scoring failed: {e}, falling back to rule-based")
            return rule_result
    
    def _combine_scores(self, rule_scores: Dict[str, float], llm_scores: Dict[str, float], weights: Dict[str, float]) -> Dict[str, float]:
        """Combine rule-based and LLM scores with weighted average"""
        
        combined = {}
        for criterion in rule_scores.keys():
            if criterion in llm_scores:
                combined[criterion] = round(
                    (rule_scores[criterion] * weights["rule"] + llm_scores[criterion] * weights["llm"]) * 2
                ) / 2
            else:
                combined[criterion] = rule_scores[criterion]
        
        return combined
    
    def _calculate_combined_confidence(self, rule_confidence: float, llm_confidence: float) -> float:
        """Calculate combined confidence score"""
        # Weight LLM confidence higher as it's more sophisticated
        return min(0.95, (rule_confidence * 0.3 + llm_confidence * 0.7))
    
    def generate_enhanced_feedback(self, essay: str, scores: Dict[str, float], prompt: str) -> str:
        """Generate enhanced feedback using LLM"""
        if self.llm_available:
            return self.llm_engine.generate_enhanced_feedback(essay, scores, prompt)
        else:
            return "Enhanced feedback requires LLM integration. Please configure API keys."
