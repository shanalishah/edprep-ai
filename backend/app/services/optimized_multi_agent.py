"""
Optimized Multi-Agent Essay Scoring System
Balanced speed and quality for IELTS essay evaluation
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from openai import OpenAI
from anthropic import Anthropic
from app.core.model_config import ModelConfig, ModelSpeed, DEFAULT_SPEED

logger = logging.getLogger(__name__)

@dataclass
class AgentResult:
    """Result from a specialized scoring agent"""
    score: float
    confidence: float
    reasoning: str
    strengths: List[str]
    weaknesses: List[str]
    specific_suggestions: List[str]
    error_analysis: List[str]

class OptimizedTaskAchievementAgent:
    """Optimized agent for Task Achievement evaluation"""
    
    def __init__(self, openai_client: Optional[OpenAI] = None, anthropic_client: Optional[Anthropic] = None, speed: ModelSpeed = DEFAULT_SPEED):
        self.openai_client = openai_client
        self.anthropic_client = anthropic_client
        self.is_available = bool(openai_client or anthropic_client)
        self.speed = speed
        self.config = ModelConfig.get_model_config(speed)
    
    def set_speed(self, speed: ModelSpeed):
        """Update speed configuration"""
        self.speed = speed
        self.config = ModelConfig.get_model_config(speed)
    
    def evaluate(self, prompt: str, essay: str, task_type: str) -> AgentResult:
        """Evaluate task achievement with optimized analysis"""
        
        if not self.is_available:
            return self._fallback_evaluation(essay, task_type)
        
        evaluation_prompt = f"""
You are an expert IELTS Writing examiner specializing in Task Achievement evaluation.

**Task Prompt:** {prompt}
**Task Type:** {task_type}
**Essay to Evaluate:** {essay}

**TASK ACHIEVEMENT EVALUATION CRITERIA:**

For Task 2:
1. **Task Response (40% weight):** Does the essay fully address all parts of the task?
2. **Position Clarity (30% weight):** Is the position clear and consistent?
3. **Idea Development (30% weight):** Are main ideas well-developed and supported?

**SCORING SCALE:** 1-9 (in 0.5 increments)

**REQUIRED JSON OUTPUT FORMAT:**
{{
    "score": 7.0,
    "confidence": 0.85,
    "reasoning": "Brief explanation of score",
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "specific_suggestions": ["suggestion1", "suggestion2"],
    "error_analysis": ["error1", "error2"]
}}
"""
        
        try:
            if self.openai_client:
                return self._evaluate_with_openai(evaluation_prompt)
            elif self.anthropic_client:
                return self._evaluate_with_anthropic(evaluation_prompt)
        except Exception as e:
            logger.error(f"Task Achievement Agent error: {e}")
            return self._fallback_evaluation(essay, task_type)
        
        return self._fallback_evaluation(essay, task_type)
    
    def _evaluate_with_openai(self, prompt: str) -> AgentResult:
        """Evaluate using OpenAI with optimized settings"""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config["openai_model"],
                messages=[
                    {"role": "system", "content": "You are an expert IELTS Writing examiner. Provide accurate evaluations in the exact JSON format requested."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"]
            )
            
            content = response.choices[0].message.content.strip()
            logger.info(f"OpenAI Task Achievement response: {content[:100]}...")
            
            # Try to parse JSON
            result = self._parse_json_response(content)
            
            # Ensure IELTS score is in 0.5 increments
            raw_score = result.get("score", 5.0)
            ielts_score = round(raw_score * 2) / 2
            ielts_score = max(1.0, min(9.0, ielts_score))
            
            return AgentResult(
                score=ielts_score,
                confidence=result.get("confidence", 0.8),
                reasoning=result.get("reasoning", "AI evaluation completed"),
                strengths=result.get("strengths", []),
                weaknesses=result.get("weaknesses", []),
                specific_suggestions=result.get("specific_suggestions", []),
                error_analysis=result.get("error_analysis", [])
            )
        except Exception as e:
            logger.error(f"Task Achievement Agent OpenAI error: {e}")
            return self._fallback_evaluation("", "Task 2")
    
    def _evaluate_with_anthropic(self, prompt: str) -> AgentResult:
        """Evaluate using Anthropic with optimized settings"""
        try:
            response = self.anthropic_client.messages.create(
                model=self.config["anthropic_model"],
                max_tokens=self.config["max_tokens"],
                temperature=self.config["temperature"],
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            logger.info(f"Anthropic Task Achievement response: {content[:100]}...")
            
            # Try to parse JSON
            result = self._parse_json_response(content)
            
            # Ensure IELTS score is in 0.5 increments
            raw_score = result.get("score", 5.0)
            ielts_score = round(raw_score * 2) / 2
            ielts_score = max(1.0, min(9.0, ielts_score))
            
            return AgentResult(
                score=ielts_score,
                confidence=result.get("confidence", 0.8),
                reasoning=result.get("reasoning", "AI evaluation completed"),
                strengths=result.get("strengths", []),
                weaknesses=result.get("weaknesses", []),
                specific_suggestions=result.get("specific_suggestions", []),
                error_analysis=result.get("error_analysis", [])
            )
        except Exception as e:
            logger.error(f"Task Achievement Agent Anthropic error: {e}")
            return self._fallback_evaluation("", "Task 2")
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON response with fallback handling"""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Return default structure if no JSON found
                return {
                    "score": 5.0,
                    "confidence": 0.7,
                    "reasoning": "Unable to parse AI response",
                    "strengths": [],
                    "weaknesses": ["Response parsing failed"],
                    "specific_suggestions": ["Try again"],
                    "error_analysis": ["JSON parsing error"]
                }
    
    def _fallback_evaluation(self, essay: str, task_type: str) -> AgentResult:
        """Fallback rule-based evaluation"""
        word_count = len(essay.split())
        
        # Simple rule-based scoring
        if word_count < 50:
            score = 3.0
            reasoning = "Insufficient length for proper task achievement"
        elif word_count < 150:
            score = 4.0
            reasoning = "Below minimum word count, limited task achievement"
        elif word_count < 250:
            score = 5.0
            reasoning = "Adequate length but may lack development"
        else:
            score = 6.0
            reasoning = "Good length for task achievement"
        
        return AgentResult(
            score=score,
            confidence=0.6,
            reasoning=reasoning,
            strengths=["Attempted the task"] if word_count > 20 else [],
            weaknesses=["Insufficient development", "Poor organization"] if word_count < 200 else [],
            specific_suggestions=["Develop ideas more fully", "Add more supporting details"],
            error_analysis=["Length below recommended minimum"] if word_count < 250 else []
        )

class OptimizedCoherenceCohesionAgent:
    """Optimized agent for Coherence and Cohesion evaluation"""
    
    def __init__(self, openai_client: Optional[OpenAI] = None, anthropic_client: Optional[Anthropic] = None, speed: ModelSpeed = DEFAULT_SPEED):
        self.openai_client = openai_client
        self.anthropic_client = anthropic_client
        self.is_available = bool(openai_client or anthropic_client)
        self.speed = speed
        self.config = ModelConfig.get_model_config(speed)
    
    def set_speed(self, speed: ModelSpeed):
        """Update speed configuration"""
        self.speed = speed
        self.config = ModelConfig.get_model_config(speed)
    
    def evaluate(self, prompt: str, essay: str, task_type: str) -> AgentResult:
        """Evaluate coherence and cohesion with optimized analysis"""
        
        if not self.is_available:
            return self._fallback_evaluation(essay)
        
        evaluation_prompt = f"""
You are an expert IELTS Writing examiner specializing in Coherence and Cohesion evaluation.

**Essay to Evaluate:** {essay}

**COHERENCE AND COHESION EVALUATION CRITERIA:**

1. **Coherence (50% weight):** Logical organization and clear progression of ideas
2. **Cohesion (50% weight):** Use of linking devices and paragraph structure

**SCORING SCALE:** 1-9 (in 0.5 increments)

**REQUIRED JSON OUTPUT FORMAT:**
{{
    "score": 7.0,
    "confidence": 0.85,
    "reasoning": "Brief explanation of score",
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "specific_suggestions": ["suggestion1", "suggestion2"],
    "error_analysis": ["error1", "error2"]
}}
"""
        
        try:
            if self.openai_client:
                return self._evaluate_with_openai(evaluation_prompt)
            elif self.anthropic_client:
                return self._evaluate_with_anthropic(evaluation_prompt)
        except Exception as e:
            logger.error(f"Coherence Agent error: {e}")
            return self._fallback_evaluation(essay)
        
        return self._fallback_evaluation(essay)
    
    def _evaluate_with_openai(self, prompt: str) -> AgentResult:
        """Evaluate using OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config["openai_model"],
                messages=[
                    {"role": "system", "content": "You are an expert IELTS Writing examiner. Provide accurate evaluations in the exact JSON format requested."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"]
            )
            
            content = response.choices[0].message.content.strip()
            result = self._parse_json_response(content)
            
            raw_score = result.get("score", 5.0)
            ielts_score = round(raw_score * 2) / 2
            ielts_score = max(1.0, min(9.0, ielts_score))
            
            return AgentResult(
                score=ielts_score,
                confidence=result.get("confidence", 0.8),
                reasoning=result.get("reasoning", "AI evaluation completed"),
                strengths=result.get("strengths", []),
                weaknesses=result.get("weaknesses", []),
                specific_suggestions=result.get("specific_suggestions", []),
                error_analysis=result.get("error_analysis", [])
            )
        except Exception as e:
            logger.error(f"Coherence Agent OpenAI error: {e}")
            return self._fallback_evaluation("")
    
    def _evaluate_with_anthropic(self, prompt: str) -> AgentResult:
        """Evaluate using Anthropic"""
        try:
            response = self.anthropic_client.messages.create(
                model=self.config["anthropic_model"],
                max_tokens=self.config["max_tokens"],
                temperature=self.config["temperature"],
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            result = self._parse_json_response(content)
            
            raw_score = result.get("score", 5.0)
            ielts_score = round(raw_score * 2) / 2
            ielts_score = max(1.0, min(9.0, ielts_score))
            
            return AgentResult(
                score=ielts_score,
                confidence=result.get("confidence", 0.8),
                reasoning=result.get("reasoning", "AI evaluation completed"),
                strengths=result.get("strengths", []),
                weaknesses=result.get("weaknesses", []),
                specific_suggestions=result.get("specific_suggestions", []),
                error_analysis=result.get("error_analysis", [])
            )
        except Exception as e:
            logger.error(f"Coherence Agent Anthropic error: {e}")
            return self._fallback_evaluation("")
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON response with fallback handling"""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "score": 5.0,
                    "confidence": 0.7,
                    "reasoning": "Unable to parse AI response",
                    "strengths": [],
                    "weaknesses": ["Response parsing failed"],
                    "specific_suggestions": ["Try again"],
                    "error_analysis": ["JSON parsing error"]
                }
    
    def _fallback_evaluation(self, essay: str) -> AgentResult:
        """Fallback rule-based evaluation"""
        sentences = essay.split('.')
        linking_words = ['however', 'therefore', 'moreover', 'furthermore', 'in addition', 'on the other hand']
        linking_count = sum(1 for word in linking_words if word in essay.lower())
        
        if linking_count == 0:
            score = 4.0
            reasoning = "No linking devices used"
        elif linking_count < 2:
            score = 5.0
            reasoning = "Limited use of linking devices"
        else:
            score = 6.0
            reasoning = "Good use of linking devices"
        
        return AgentResult(
            score=score,
            confidence=0.6,
            reasoning=reasoning,
            strengths=["Some linking devices used"] if linking_count > 0 else [],
            weaknesses=["Poor paragraph structure", "Limited linking devices"],
            specific_suggestions=["Add more linking words", "Improve paragraph structure"],
            error_analysis=["Low sentence complexity", "Poor organization"]
        )

class OptimizedLexicalResourceAgent:
    """Optimized agent for Lexical Resource evaluation"""
    
    def __init__(self, openai_client: Optional[OpenAI] = None, anthropic_client: Optional[Anthropic] = None, speed: ModelSpeed = DEFAULT_SPEED):
        self.openai_client = openai_client
        self.anthropic_client = anthropic_client
        self.is_available = bool(openai_client or anthropic_client)
        self.speed = speed
        self.config = ModelConfig.get_model_config(speed)
    
    def set_speed(self, speed: ModelSpeed):
        """Update speed configuration"""
        self.speed = speed
        self.config = ModelConfig.get_model_config(speed)
    
    def evaluate(self, prompt: str, essay: str, task_type: str) -> AgentResult:
        """Evaluate lexical resource with optimized analysis"""
        
        if not self.is_available:
            return self._fallback_evaluation(essay)
        
        evaluation_prompt = f"""
You are an expert IELTS Writing examiner specializing in Lexical Resource evaluation.

**Essay to Evaluate:** {essay}

**LEXICAL RESOURCE EVALUATION CRITERIA:**

1. **Vocabulary Range (40% weight):** Variety and appropriateness of vocabulary
2. **Word Choice (30% weight):** Precision and accuracy of word usage
3. **Collocation (30% weight):** Natural word combinations and idiomatic expressions

**SCORING SCALE:** 1-9 (in 0.5 increments)

**REQUIRED JSON OUTPUT FORMAT:**
{{
    "score": 7.0,
    "confidence": 0.85,
    "reasoning": "Brief explanation of score",
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "specific_suggestions": ["suggestion1", "suggestion2"],
    "error_analysis": ["error1", "error2"]
}}
"""
        
        try:
            if self.openai_client:
                return self._evaluate_with_openai(evaluation_prompt)
            elif self.anthropic_client:
                return self._evaluate_with_anthropic(evaluation_prompt)
        except Exception as e:
            logger.error(f"Lexical Agent error: {e}")
            return self._fallback_evaluation(essay)
        
        return self._fallback_evaluation(essay)
    
    def _evaluate_with_openai(self, prompt: str) -> AgentResult:
        """Evaluate using OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config["openai_model"],
                messages=[
                    {"role": "system", "content": "You are an expert IELTS Writing examiner. Provide accurate evaluations in the exact JSON format requested."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"]
            )
            
            content = response.choices[0].message.content.strip()
            result = self._parse_json_response(content)
            
            raw_score = result.get("score", 5.0)
            ielts_score = round(raw_score * 2) / 2
            ielts_score = max(1.0, min(9.0, ielts_score))
            
            return AgentResult(
                score=ielts_score,
                confidence=result.get("confidence", 0.8),
                reasoning=result.get("reasoning", "AI evaluation completed"),
                strengths=result.get("strengths", []),
                weaknesses=result.get("weaknesses", []),
                specific_suggestions=result.get("specific_suggestions", []),
                error_analysis=result.get("error_analysis", [])
            )
        except Exception as e:
            logger.error(f"Lexical Agent OpenAI error: {e}")
            return self._fallback_evaluation("")
    
    def _evaluate_with_anthropic(self, prompt: str) -> AgentResult:
        """Evaluate using Anthropic"""
        try:
            response = self.anthropic_client.messages.create(
                model=self.config["anthropic_model"],
                max_tokens=self.config["max_tokens"],
                temperature=self.config["temperature"],
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            result = self._parse_json_response(content)
            
            raw_score = result.get("score", 5.0)
            ielts_score = round(raw_score * 2) / 2
            ielts_score = max(1.0, min(9.0, ielts_score))
            
            return AgentResult(
                score=ielts_score,
                confidence=result.get("confidence", 0.8),
                reasoning=result.get("reasoning", "AI evaluation completed"),
                strengths=result.get("strengths", []),
                weaknesses=result.get("weaknesses", []),
                specific_suggestions=result.get("specific_suggestions", []),
                error_analysis=result.get("error_analysis", [])
            )
        except Exception as e:
            logger.error(f"Lexical Agent Anthropic error: {e}")
            return self._fallback_evaluation("")
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON response with fallback handling"""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "score": 5.0,
                    "confidence": 0.7,
                    "reasoning": "Unable to parse AI response",
                    "strengths": [],
                    "weaknesses": ["Response parsing failed"],
                    "specific_suggestions": ["Try again"],
                    "error_analysis": ["JSON parsing error"]
                }
    
    def _fallback_evaluation(self, essay: str) -> AgentResult:
        """Fallback rule-based evaluation"""
        words = essay.split()
        unique_words = len(set(word.lower() for word in words))
        lexical_diversity = unique_words / len(words) if words else 0
        
        if lexical_diversity < 0.3:
            score = 4.0
            reasoning = "Limited vocabulary range"
        elif lexical_diversity < 0.5:
            score = 5.0
            reasoning = "Adequate vocabulary range"
        else:
            score = 6.0
            reasoning = "Good vocabulary range"
        
        return AgentResult(
            score=score,
            confidence=0.6,
            reasoning=reasoning,
            strengths=["Some variety in vocabulary"] if lexical_diversity > 0.3 else [],
            weaknesses=["Limited vocabulary range", "Repetitive word choice"],
            specific_suggestions=["Use more varied vocabulary", "Learn synonyms"],
            error_analysis=["Low lexical diversity", "Limited vocabulary range"]
        )

class OptimizedGrammaticalRangeAgent:
    """Optimized agent for Grammatical Range and Accuracy evaluation"""
    
    def __init__(self, openai_client: Optional[OpenAI] = None, anthropic_client: Optional[Anthropic] = None, speed: ModelSpeed = DEFAULT_SPEED):
        self.openai_client = openai_client
        self.anthropic_client = anthropic_client
        self.is_available = bool(openai_client or anthropic_client)
        self.speed = speed
        self.config = ModelConfig.get_model_config(speed)
    
    def set_speed(self, speed: ModelSpeed):
        """Update speed configuration"""
        self.speed = speed
        self.config = ModelConfig.get_model_config(speed)
    
    def evaluate(self, prompt: str, essay: str, task_type: str) -> AgentResult:
        """Evaluate grammatical range and accuracy with optimized analysis"""
        
        if not self.is_available:
            return self._fallback_evaluation(essay)
        
        evaluation_prompt = f"""
You are an expert IELTS Writing examiner specializing in Grammatical Range and Accuracy evaluation.

**Essay to Evaluate:** {essay}

**GRAMMATICAL RANGE AND ACCURACY EVALUATION CRITERIA:**

1. **Range (50% weight):** Variety of sentence structures and grammatical forms
2. **Accuracy (50% weight):** Correct use of grammar and punctuation

**SCORING SCALE:** 1-9 (in 0.5 increments)

**REQUIRED JSON OUTPUT FORMAT:**
{{
    "score": 7.0,
    "confidence": 0.85,
    "reasoning": "Brief explanation of score",
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "specific_suggestions": ["suggestion1", "suggestion2"],
    "error_analysis": ["error1", "error2"]
}}
"""
        
        try:
            if self.openai_client:
                return self._evaluate_with_openai(evaluation_prompt)
            elif self.anthropic_client:
                return self._evaluate_with_anthropic(evaluation_prompt)
        except Exception as e:
            logger.error(f"Grammar Agent error: {e}")
            return self._fallback_evaluation(essay)
        
        return self._fallback_evaluation(essay)
    
    def _evaluate_with_openai(self, prompt: str) -> AgentResult:
        """Evaluate using OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config["openai_model"],
                messages=[
                    {"role": "system", "content": "You are an expert IELTS Writing examiner. Provide accurate evaluations in the exact JSON format requested."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"]
            )
            
            content = response.choices[0].message.content.strip()
            result = self._parse_json_response(content)
            
            raw_score = result.get("score", 5.0)
            ielts_score = round(raw_score * 2) / 2
            ielts_score = max(1.0, min(9.0, ielts_score))
            
            return AgentResult(
                score=ielts_score,
                confidence=result.get("confidence", 0.8),
                reasoning=result.get("reasoning", "AI evaluation completed"),
                strengths=result.get("strengths", []),
                weaknesses=result.get("weaknesses", []),
                specific_suggestions=result.get("specific_suggestions", []),
                error_analysis=result.get("error_analysis", [])
            )
        except Exception as e:
            logger.error(f"Grammar Agent OpenAI error: {e}")
            return self._fallback_evaluation("")
    
    def _evaluate_with_anthropic(self, prompt: str) -> AgentResult:
        """Evaluate using Anthropic"""
        try:
            response = self.anthropic_client.messages.create(
                model=self.config["anthropic_model"],
                max_tokens=self.config["max_tokens"],
                temperature=self.config["temperature"],
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            result = self._parse_json_response(content)
            
            raw_score = result.get("score", 5.0)
            ielts_score = round(raw_score * 2) / 2
            ielts_score = max(1.0, min(9.0, ielts_score))
            
            return AgentResult(
                score=ielts_score,
                confidence=result.get("confidence", 0.8),
                reasoning=result.get("reasoning", "AI evaluation completed"),
                strengths=result.get("strengths", []),
                weaknesses=result.get("weaknesses", []),
                specific_suggestions=result.get("specific_suggestions", []),
                error_analysis=result.get("error_analysis", [])
            )
        except Exception as e:
            logger.error(f"Grammar Agent Anthropic error: {e}")
            return self._fallback_evaluation("")
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON response with fallback handling"""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "score": 5.0,
                    "confidence": 0.7,
                    "reasoning": "Unable to parse AI response",
                    "strengths": [],
                    "weaknesses": ["Response parsing failed"],
                    "specific_suggestions": ["Try again"],
                    "error_analysis": ["JSON parsing error"]
                }
    
    def _fallback_evaluation(self, essay: str) -> AgentResult:
        """Fallback rule-based evaluation"""
        sentences = essay.split('.')
        complex_sentences = sum(1 for s in sentences if ',' in s or ';' in s)
        sentence_complexity = complex_sentences / len(sentences) if sentences else 0
        
        if sentence_complexity < 0.2:
            score = 4.0
            reasoning = "Limited sentence variety"
        elif sentence_complexity < 0.4:
            score = 5.0
            reasoning = "Adequate sentence variety"
        else:
            score = 6.0
            reasoning = "Good sentence variety"
        
        return AgentResult(
            score=score,
            confidence=0.6,
            reasoning=reasoning,
            strengths=["Some sentence variety"] if sentence_complexity > 0.2 else [],
            weaknesses=["Limited sentence variety", "Simple sentence structures"],
            specific_suggestions=["Use more complex sentences", "Vary sentence structures"],
            error_analysis=["Low sentence complexity", "Limited grammatical range"]
        )

class OptimizedMultiAgentScoringEngine:
    """Optimized Multi-Agent Essay Scoring Engine"""
    
    def __init__(self, openai_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None, speed: ModelSpeed = DEFAULT_SPEED):
        self.openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
        self.anthropic_client = Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        self.is_available = bool(openai_api_key or anthropic_api_key)
        self.speed = speed
        self._update_agent_models()

        self.task_achievement_agent = OptimizedTaskAchievementAgent(self.openai_client, self.anthropic_client, self.speed)
        self.coherence_agent = OptimizedCoherenceCohesionAgent(self.openai_client, self.anthropic_client, self.speed)
        self.lexical_agent = OptimizedLexicalResourceAgent(self.openai_client, self.anthropic_client, self.speed)
        self.grammar_agent = OptimizedGrammaticalRangeAgent(self.openai_client, self.anthropic_client, self.speed)

        if not self.is_available:
            logger.warning("⚠️ No LLM API keys provided, Optimized Multi-Agent Scoring Engine will use fallback.")

    def _update_agent_models(self):
        """Update model configurations for all agents"""
        config = ModelConfig.get_model_config(self.speed)
        self.openai_model = config["openai_model"]
        self.anthropic_model = config["anthropic_model"]
        self.openai_max_tokens = config["max_tokens"]
        self.anthropic_max_tokens = config["max_tokens"]
        self.temperature = config["temperature"]
        logger.info(f"OptimizedMultiAgentScoringEngine updated to {self.speed.value} mode. OpenAI: {self.openai_model}, Anthropic: {self.anthropic_model}")

    def set_speed(self, speed: ModelSpeed):
        """Update speed configuration for all agents"""
        self.speed = speed
        self._update_agent_models()
        self.task_achievement_agent.set_speed(speed)
        self.coherence_agent.set_speed(speed)
        self.lexical_agent.set_speed(speed)
        self.grammar_agent.set_speed(speed)

    def score_essay(self, prompt: str, essay: str, task_type: str) -> Dict[str, Any]:
        """Score essay using multiple specialized agents"""
        if not self.is_available:
            logger.warning("LLM API keys not available, using fallback for optimized engine.")
            return self._fallback_scoring(essay, task_type)

        start_time = asyncio.get_event_loop().time() if hasattr(asyncio, 'get_event_loop') else 0

        try:
            # Run agents sequentially for now to avoid asyncio conflicts
            results = {}
            
            try:
                results["task_achievement"] = self.task_achievement_agent.evaluate(prompt, essay, task_type)
            except Exception as e:
                logger.error(f"Task Achievement Agent error: {e}")
                results["task_achievement"] = self.task_achievement_agent._fallback_evaluation(essay, task_type)
            
            try:
                results["coherence_cohesion"] = self.coherence_agent.evaluate(prompt, essay, task_type)
            except Exception as e:
                logger.error(f"Coherence Agent error: {e}")
                results["coherence_cohesion"] = self.coherence_agent._fallback_evaluation(essay)
            
            try:
                results["lexical_resource"] = self.lexical_agent.evaluate(prompt, essay, task_type)
            except Exception as e:
                logger.error(f"Lexical Agent error: {e}")
                results["lexical_resource"] = self.lexical_agent._fallback_evaluation(essay)
            
            try:
                results["grammatical_range"] = self.grammar_agent.evaluate(prompt, essay, task_type)
            except Exception as e:
                logger.error(f"Grammar Agent error: {e}")
                results["grammatical_range"] = self.grammar_agent._fallback_evaluation(essay)

            # Aggregate scores and feedback
            aggregated_scores = {
                "task_achievement": results["task_achievement"].score,
                "coherence_cohesion": results["coherence_cohesion"].score,
                "lexical_resource": results["lexical_resource"].score,
                "grammatical_range": results["grammatical_range"].score,
            }
            overall_band_score = round(sum(aggregated_scores.values()) / len(aggregated_scores), 1)

            all_strengths = []
            all_weaknesses = []
            all_suggestions = []
            all_error_analysis = []

            for agent_result in results.values():
                all_strengths.extend(agent_result.strengths)
                all_weaknesses.extend(agent_result.weaknesses)
                all_suggestions.extend(agent_result.specific_suggestions)
                all_error_analysis.extend(agent_result.error_analysis)

            end_time = asyncio.get_event_loop().time() if hasattr(asyncio, 'get_event_loop') else 0
            processing_time = end_time - start_time if start_time else 0

            return {
                "scores": aggregated_scores,
                "overall_band_score": overall_band_score,
                "feedback": {
                    "strengths": list(set(all_strengths)),
                    "weaknesses": list(set(all_weaknesses)),
                    "suggestions": list(set(all_suggestions)),
                    "error_analysis": list(set(all_error_analysis)),
                },
                "assessment_method": f"optimized_multi_agent_{self.speed.value}",
                "processing_time_seconds": processing_time,
                "confidence": round(sum(r.confidence for r in results.values()) / len(results), 2)
            }

        except Exception as e:
            logger.error(f"❌ Optimized Multi-Agent Scoring Engine failed: {e}")
            return self._fallback_scoring(essay, task_type, error_detail=str(e))

    def _fallback_scoring(self, essay: str, task_type: str, error_detail: str = "") -> Dict[str, Any]:
        """Fallback scoring when AI is not available"""
        word_count = len(essay.split())
        
        # Simple fallback scoring
        if word_count < 50:
            base_score = 3.0
        elif word_count < 150:
            base_score = 4.0
        elif word_count < 250:
            base_score = 5.0
        else:
            base_score = 6.0
        
        scores = {
            "task_achievement": base_score,
            "coherence_cohesion": base_score,
            "lexical_resource": base_score,
            "grammatical_range": base_score,
        }
        
        return {
            "scores": scores,
            "overall_band_score": base_score,
            "feedback": {
                "strengths": ["Attempted the task"] if word_count > 20 else [],
                "weaknesses": ["Insufficient development", "Poor organization"] if word_count < 200 else [],
                "suggestions": ["Develop ideas more fully", "Add more supporting details"],
                "error_analysis": ["Length below recommended minimum"] if word_count < 250 else []
            },
            "assessment_method": f"fallback_{self.speed.value}",
            "processing_time_seconds": 0.1,
            "confidence": 0.6,
            "error_detail": error_detail
        }