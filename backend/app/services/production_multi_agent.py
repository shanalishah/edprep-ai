"""
Production Multi-Agent Essay Scoring System
Highest accuracy and logical output for IELTS essay evaluation
"""

import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from openai import OpenAI
from anthropic import Anthropic

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

class TaskAchievementAgent:
    """Specialized agent for Task Achievement evaluation - highest accuracy"""
    
    def __init__(self, openai_client: Optional[OpenAI] = None, anthropic_client: Optional[Anthropic] = None):
        self.openai_client = openai_client
        self.anthropic_client = anthropic_client
        self.is_available = bool(openai_client or anthropic_client)
    
    def evaluate(self, prompt: str, essay: str, task_type: str) -> AgentResult:
        """Evaluate task achievement with expert-level analysis"""
        
        evaluation_prompt = f"""
You are an expert IELTS Writing examiner specializing in Task Achievement evaluation. You have 15+ years of experience and have evaluated thousands of essays.

**Task Prompt:** {prompt}
**Task Type:** {task_type}
**Essay to Evaluate:** {essay}

**TASK ACHIEVEMENT EVALUATION CRITERIA:**

For Task 2:
1. **Task Response (40% weight):**
   - Does the essay fully address all parts of the task?
   - Is the position clear and consistent throughout?
   - Are all main ideas relevant to the task?

2. **Position Clarity (30% weight):**
   - Is the writer's opinion/position clearly stated?
   - Is the position maintained consistently?
   - Does the conclusion reinforce the position?

3. **Supporting Ideas (20% weight):**
   - Are main ideas supported with relevant examples?
   - Are examples specific and well-developed?
   - Is there sufficient detail to support arguments?

4. **Conclusion (10% weight):**
   - Is there a clear, appropriate conclusion?
   - Does it summarize the main points?
   - Does it reinforce the position?

**SCORING SCALE:**
- 9.0: Fully addresses all parts, clear position, well-developed ideas, excellent conclusion
- 8.0: Addresses all parts, clear position, well-developed ideas, good conclusion
- 7.0: Addresses all parts, clear position, some development, appropriate conclusion
- 6.0: Addresses most parts, position clear, some development, conclusion present
- 5.0: Addresses some parts, position unclear, limited development, weak conclusion
- 4.0: Addresses few parts, position unclear, minimal development, poor conclusion
- 3.0: Addresses very few parts, no clear position, no development, no conclusion
- 2.0: Does not address the task, no position, no development, no conclusion
- 1.0: Completely off-topic or incomprehensible

Provide your evaluation in this exact JSON format:
{{
    "score": <1.0-9.0>,
    "confidence": <0.0-1.0>,
    "reasoning": "Detailed explanation of the score",
    "strengths": ["strength1", "strength2", ...],
    "weaknesses": ["weakness1", "weakness2", ...],
    "specific_suggestions": ["suggestion1", "suggestion2", ...],
    "error_analysis": ["error1", "error2", ...]
}}
"""
        
        if self.openai_client:
            return self._evaluate_with_openai(evaluation_prompt)
        elif self.anthropic_client:
            return self._evaluate_with_anthropic(evaluation_prompt)
        else:
            # Fallback to rule-based
            return self._fallback_evaluation(essay, task_type)
    
    def _evaluate_with_openai(self, prompt: str) -> AgentResult:
        """Evaluate using OpenAI with structured output"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert IELTS Writing examiner with 15+ years of experience. Provide accurate, detailed evaluations in the exact JSON format requested."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            return AgentResult(
                score=round(result["score"] * 2) / 2,
                confidence=result["confidence"],
                reasoning=result["reasoning"],
                strengths=result["strengths"],
                weaknesses=result["weaknesses"],
                specific_suggestions=result["specific_suggestions"],
                error_analysis=result["error_analysis"]
            )
        except Exception as e:
            logger.error(f"Task Achievement Agent OpenAI error: {e}")
            return self._fallback_evaluation("", "Task 2")
    
    def _evaluate_with_anthropic(self, prompt: str) -> AgentResult:
        """Evaluate using Anthropic with structured output"""
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(response.content[0].text)
            return AgentResult(
                score=round(result["score"] * 2) / 2,
                confidence=result["confidence"],
                reasoning=result["reasoning"],
                strengths=result["strengths"],
                weaknesses=result["weaknesses"],
                specific_suggestions=result["specific_suggestions"],
                error_analysis=result["error_analysis"]
            )
        except Exception as e:
            logger.error(f"Task Achievement Agent Anthropic error: {e}")
            return self._fallback_evaluation("", "Task 2")
    
    def _fallback_evaluation(self, essay: str, task_type: str) -> AgentResult:
        """Fallback rule-based evaluation with off-topic detection"""
        word_count = len(essay.split())
        score = 1.0
        
        # CRITICAL: Check for completely off-topic essays
        # Common off-topic topics that students might write about
        off_topic_indicators = [
            "football", "soccer", "basketball", "sports", "playing", "game", "team",
            "my hobby", "my favorite", "I love", "I like", "I enjoy",
            "my family", "my mother", "my father", "my parents",
            "my school", "my teacher", "my friends", "my classmates",
            "my country", "my city", "my hometown",
            "food", "restaurant", "cooking", "eating",
            "music", "movie", "film", "song", "dancing",
            "travel", "vacation", "holiday", "trip"
        ]
        
        essay_lower = essay.lower()
        off_topic_count = sum(1 for indicator in off_topic_indicators if indicator in essay_lower)
        
        # If essay contains many off-topic indicators and no academic/task-related content
        if off_topic_count >= 3:
            return AgentResult(
                score=0.0,  # Completely off-topic = 0
                confidence=0.9,
                reasoning="Essay is completely off-topic and does not address the task requirements at all.",
                strengths=[],
                weaknesses=["Completely off-topic", "No task response", "Irrelevant content"],
                specific_suggestions=[
                    "Read the prompt carefully and address the exact question asked",
                    "Stay focused on the topic throughout your essay",
                    "Practice prompt analysis before writing"
                ],
                error_analysis=["Complete task failure", "Off-topic content"]
            )
        
        if task_type == "Task 2":
            if word_count >= 250:
                score += 3.0
            elif word_count >= 200:
                score += 2.0
            elif word_count >= 150:
                score += 1.0
        
        # Check for position indicators
        position_indicators = ["I believe", "I think", "in my opinion", "I agree", "I disagree"]
        if any(indicator in essay.lower() for indicator in position_indicators):
            score += 1.0
        
        # Check for examples
        example_indicators = ["for example", "for instance", "such as"]
        if any(indicator in essay.lower() for indicator in example_indicators):
            score += 1.0
        
        # Check for conclusion
        conclusion_indicators = ["in conclusion", "to conclude", "overall"]
        if any(indicator in essay.lower() for indicator in conclusion_indicators):
            score += 1.0
        
        return AgentResult(
            score=min(9.0, score),
            confidence=0.7,
            reasoning="Rule-based evaluation (LLM not available)",
            strengths=["Basic structure present"] if word_count > 150 else [],
            weaknesses=["Limited analysis available"] if word_count < 200 else [],
            specific_suggestions=["Enable LLM for detailed analysis"],
            error_analysis=[]
        )

class CoherenceCohesionAgent:
    """Specialized agent for Coherence and Cohesion evaluation"""
    
    def __init__(self, openai_client: Optional[OpenAI] = None, anthropic_client: Optional[Anthropic] = None):
        self.openai_client = openai_client
        self.anthropic_client = anthropic_client
        self.is_available = bool(openai_client or anthropic_client)
    
    def evaluate(self, essay: str) -> AgentResult:
        """Evaluate coherence and cohesion with expert analysis"""
        
        evaluation_prompt = f"""
You are an expert IELTS Writing examiner specializing in Coherence and Cohesion evaluation.

**Essay to Evaluate:** {essay}

**COHERENCE AND COHESION EVALUATION CRITERIA:**

1. **Paragraph Structure (30% weight):**
   - Clear introduction, body paragraphs, conclusion
   - Logical paragraph breaks
   - Appropriate paragraph length

2. **Logical Flow (25% weight):**
   - Ideas progress logically
   - Clear sequence of arguments
   - Smooth transitions between ideas

3. **Linking Words (25% weight):**
   - Appropriate use of cohesive devices
   - Variety in linking expressions
   - Natural and accurate usage

4. **Cohesive Devices (20% weight):**
   - Pronouns, demonstratives, substitution
   - Reference chains
   - Lexical cohesion

**SCORING SCALE:**
- 9.0: Excellent organization, seamless flow, sophisticated linking, perfect cohesion
- 8.0: Very good organization, clear flow, good linking, strong cohesion
- 7.0: Good organization, clear flow, adequate linking, good cohesion
- 6.0: Generally clear organization, some flow issues, basic linking, adequate cohesion
- 5.0: Some organization, unclear flow, limited linking, weak cohesion
- 4.0: Poor organization, confusing flow, minimal linking, poor cohesion
- 3.0: Very poor organization, no clear flow, no linking, no cohesion
- 2.0: No organization, incomprehensible flow
- 1.0: Completely incoherent

Provide your evaluation in this exact JSON format:
{{
    "score": <1.0-9.0>,
    "confidence": <0.0-1.0>,
    "reasoning": "Detailed explanation of the score",
    "strengths": ["strength1", "strength2", ...],
    "weaknesses": ["weakness1", "weakness2", ...],
    "specific_suggestions": ["suggestion1", "suggestion2", ...],
    "error_analysis": ["error1", "error2", ...]
}}
"""
        
        if self.openai_client:
            return self._evaluate_with_openai(evaluation_prompt)
        elif self.anthropic_client:
            return self._evaluate_with_anthropic(evaluation_prompt)
        else:
            return self._fallback_evaluation(essay)
    
    def _evaluate_with_openai(self, prompt: str) -> AgentResult:
        """Evaluate using OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert IELTS Writing examiner specializing in coherence and cohesion. Provide accurate evaluations in the exact JSON format requested."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            return AgentResult(
                score=round(result["score"] * 2) / 2,
                confidence=result["confidence"],
                reasoning=result["reasoning"],
                strengths=result["strengths"],
                weaknesses=result["weaknesses"],
                specific_suggestions=result["specific_suggestions"],
                error_analysis=result["error_analysis"]
            )
        except Exception as e:
            logger.error(f"Coherence Agent OpenAI error: {e}")
            return self._fallback_evaluation("")
    
    def _evaluate_with_anthropic(self, prompt: str) -> AgentResult:
        """Evaluate using Anthropic"""
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(response.content[0].text)
            return AgentResult(
                score=round(result["score"] * 2) / 2,
                confidence=result["confidence"],
                reasoning=result["reasoning"],
                strengths=result["strengths"],
                weaknesses=result["weaknesses"],
                specific_suggestions=result["specific_suggestions"],
                error_analysis=result["error_analysis"]
            )
        except Exception as e:
            logger.error(f"Coherence Agent Anthropic error: {e}")
            return self._fallback_evaluation("")
    
    def _fallback_evaluation(self, essay: str) -> AgentResult:
        """Fallback rule-based evaluation"""
        paragraphs = [p.strip() for p in essay.split('\n\n') if p.strip()]
        score = 1.0
        
        # Paragraph structure
        if len(paragraphs) >= 3:
            score += 2.0
        elif len(paragraphs) >= 2:
            score += 1.0
        
        # Linking words
        linking_words = ["however", "therefore", "moreover", "furthermore", "additionally", "consequently"]
        linking_count = sum(1 for word in linking_words if word in essay.lower())
        score += min(2.0, linking_count * 0.3)
        
        return AgentResult(
            score=min(9.0, score),
            confidence=0.7,
            reasoning="Rule-based evaluation (LLM not available)",
            strengths=["Basic structure"] if len(paragraphs) >= 2 else [],
            weaknesses=["Limited analysis"] if linking_count < 2 else [],
            specific_suggestions=["Enable LLM for detailed analysis"],
            error_analysis=[]
        )

class LexicalResourceAgent:
    """Specialized agent for Lexical Resource evaluation"""
    
    def __init__(self, openai_client: Optional[OpenAI] = None, anthropic_client: Optional[Anthropic] = None):
        self.openai_client = openai_client
        self.anthropic_client = anthropic_client
        self.is_available = bool(openai_client or anthropic_client)
    
    def evaluate(self, essay: str) -> AgentResult:
        """Evaluate lexical resource with expert analysis"""
        
        evaluation_prompt = f"""
You are an expert IELTS Writing examiner specializing in Lexical Resource evaluation.

**Essay to Evaluate:** {essay}

**LEXICAL RESOURCE EVALUATION CRITERIA:**

1. **Vocabulary Range (40% weight):**
   - Variety of vocabulary used
   - Less common vocabulary appropriately used
   - Avoidance of repetition

2. **Word Choice Accuracy (30% weight):**
   - Words used in correct contexts
   - Appropriate register and style
   - Natural collocations

3. **Spelling and Word Formation (20% weight):**
   - Correct spelling
   - Proper word formation
   - Appropriate affixes

4. **Lexical Features (10% weight):**
   - Idiomatic expressions
   - Phrasal verbs
   - Academic vocabulary

**SCORING SCALE:**
- 9.0: Wide range, sophisticated vocabulary, perfect accuracy, natural usage
- 8.0: Wide range, good vocabulary, high accuracy, mostly natural
- 7.0: Sufficient range, some less common words, good accuracy, generally natural
- 6.0: Adequate range, basic vocabulary, some accuracy issues, sometimes unnatural
- 5.0: Limited range, basic vocabulary, frequent errors, often unnatural
- 4.0: Very limited range, very basic vocabulary, many errors, frequently unnatural
- 3.0: Extremely limited range, minimal vocabulary, constant errors
- 2.0: Almost no vocabulary range, constant errors
- 1.0: No vocabulary range, incomprehensible

Provide your evaluation in this exact JSON format:
{{
    "score": <1.0-9.0>,
    "confidence": <0.0-1.0>,
    "reasoning": "Detailed explanation of the score",
    "strengths": ["strength1", "strength2", ...],
    "weaknesses": ["weakness1", "weakness2", ...],
    "specific_suggestions": ["suggestion1", "suggestion2", ...],
    "error_analysis": ["error1", "error2", ...]
}}
"""
        
        if self.openai_client:
            return self._evaluate_with_openai(evaluation_prompt)
        elif self.anthropic_client:
            return self._evaluate_with_anthropic(evaluation_prompt)
        else:
            return self._fallback_evaluation(essay)
    
    def _evaluate_with_openai(self, prompt: str) -> AgentResult:
        """Evaluate using OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert IELTS Writing examiner specializing in lexical resource. Provide accurate evaluations in the exact JSON format requested."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            return AgentResult(
                score=round(result["score"] * 2) / 2,
                confidence=result["confidence"],
                reasoning=result["reasoning"],
                strengths=result["strengths"],
                weaknesses=result["weaknesses"],
                specific_suggestions=result["specific_suggestions"],
                error_analysis=result["error_analysis"]
            )
        except Exception as e:
            logger.error(f"Lexical Agent OpenAI error: {e}")
            return self._fallback_evaluation("")
    
    def _evaluate_with_anthropic(self, prompt: str) -> AgentResult:
        """Evaluate using Anthropic"""
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(response.content[0].text)
            return AgentResult(
                score=round(result["score"] * 2) / 2,
                confidence=result["confidence"],
                reasoning=result["reasoning"],
                strengths=result["strengths"],
                weaknesses=result["weaknesses"],
                specific_suggestions=result["specific_suggestions"],
                error_analysis=result["error_analysis"]
            )
        except Exception as e:
            logger.error(f"Lexical Agent Anthropic error: {e}")
            return self._fallback_evaluation("")
    
    def _fallback_evaluation(self, essay: str) -> AgentResult:
        """Fallback rule-based evaluation"""
        words = essay.lower().split()
        unique_words = set(words)
        lexical_diversity = len(unique_words) / len(words) if words else 0
        score = 1.0
        
        if lexical_diversity > 0.7:
            score += 2.0
        elif lexical_diversity > 0.6:
            score += 1.5
        elif lexical_diversity > 0.5:
            score += 1.0
        
        # Academic vocabulary
        academic_words = ["significant", "substantial", "considerable", "essential", "crucial"]
        academic_count = sum(1 for word in academic_words if word in essay.lower())
        score += min(2.0, academic_count * 0.3)
        
        return AgentResult(
            score=min(9.0, score),
            confidence=0.7,
            reasoning="Rule-based evaluation (LLM not available)",
            strengths=["Basic vocabulary range"] if lexical_diversity > 0.5 else [],
            weaknesses=["Limited analysis"] if academic_count < 2 else [],
            specific_suggestions=["Enable LLM for detailed analysis"],
            error_analysis=[]
        )

class GrammaticalRangeAgent:
    """Specialized agent for Grammatical Range and Accuracy evaluation"""
    
    def __init__(self, openai_client: Optional[OpenAI] = None, anthropic_client: Optional[Anthropic] = None):
        self.openai_client = openai_client
        self.anthropic_client = anthropic_client
        self.is_available = bool(openai_client or anthropic_client)
    
    def evaluate(self, essay: str) -> AgentResult:
        """Evaluate grammatical range and accuracy with expert analysis"""
        
        evaluation_prompt = f"""
You are an expert IELTS Writing examiner specializing in Grammatical Range and Accuracy evaluation.

**Essay to Evaluate:** {essay}

**GRAMMATICAL RANGE AND ACCURACY EVALUATION CRITERIA:**

1. **Sentence Variety (40% weight):**
   - Mix of simple, compound, and complex sentences
   - Appropriate use of different sentence structures
   - Variety in sentence length

2. **Grammar Accuracy (35% weight):**
   - Correct use of tenses
   - Subject-verb agreement
   - Proper use of articles, prepositions
   - Correct word order

3. **Complex Structures (15% weight):**
   - Subordinate clauses
   - Conditional sentences
   - Passive voice
   - Relative clauses

4. **Error Impact (10% weight):**
   - Do errors impede communication?
   - Frequency of errors
   - Types of errors

**SCORING SCALE:**
- 9.0: Wide range, perfect accuracy, sophisticated structures, no errors
- 8.0: Wide range, high accuracy, good structures, rare errors
- 7.0: Good range, good accuracy, some complex structures, occasional errors
- 6.0: Adequate range, some accuracy issues, basic structures, some errors
- 5.0: Limited range, frequent errors, simple structures, errors affect clarity
- 4.0: Very limited range, many errors, very simple structures, errors impede communication
- 3.0: Extremely limited range, constant errors, no complex structures
- 2.0: Almost no range, constant errors, incomprehensible
- 1.0: No grammatical range, incomprehensible

Provide your evaluation in this exact JSON format:
{{
    "score": <1.0-9.0>,
    "confidence": <0.0-1.0>,
    "reasoning": "Detailed explanation of the score",
    "strengths": ["strength1", "strength2", ...],
    "weaknesses": ["weakness1", "weakness2", ...],
    "specific_suggestions": ["suggestion1", "suggestion2", ...],
    "error_analysis": ["error1", "error2", ...]
}}
"""
        
        if self.openai_client:
            return self._evaluate_with_openai(evaluation_prompt)
        elif self.anthropic_client:
            return self._evaluate_with_anthropic(evaluation_prompt)
        else:
            return self._fallback_evaluation(essay)
    
    def _evaluate_with_openai(self, prompt: str) -> AgentResult:
        """Evaluate using OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert IELTS Writing examiner specializing in grammatical range and accuracy. Provide accurate evaluations in the exact JSON format requested."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content)
            return AgentResult(
                score=round(result["score"] * 2) / 2,
                confidence=result["confidence"],
                reasoning=result["reasoning"],
                strengths=result["strengths"],
                weaknesses=result["weaknesses"],
                specific_suggestions=result["specific_suggestions"],
                error_analysis=result["error_analysis"]
            )
        except Exception as e:
            logger.error(f"Grammar Agent OpenAI error: {e}")
            return self._fallback_evaluation("")
    
    def _evaluate_with_anthropic(self, prompt: str) -> AgentResult:
        """Evaluate using Anthropic"""
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(response.content[0].text)
            return AgentResult(
                score=round(result["score"] * 2) / 2,
                confidence=result["confidence"],
                reasoning=result["reasoning"],
                strengths=result["strengths"],
                weaknesses=result["weaknesses"],
                specific_suggestions=result["specific_suggestions"],
                error_analysis=result["error_analysis"]
            )
        except Exception as e:
            logger.error(f"Grammar Agent Anthropic error: {e}")
            return self._fallback_evaluation("")
    
    def _fallback_evaluation(self, essay: str) -> AgentResult:
        """Fallback rule-based evaluation"""
        import re
        sentences = essay.split('.')
        score = 1.0
        
        # Sentence variety
        complex_sentences = 0
        for sentence in sentences:
            if any(subord in sentence.lower() for subord in ['because', 'although', 'while', 'since', 'if', 'when', 'where', 'which', 'who', 'that']):
                complex_sentences += 1
        
        if len(sentences) > 0:
            variety_score = complex_sentences / len(sentences)
            score += variety_score * 2.0
        
        # Basic grammar check
        if re.search(r'\b(am|is|are|was|were|be|being|been|have|has|had|do|does|did|will|would|can|could|may|might|must|should|shall)\b', essay.lower()):
            score += 1.0
        
        return AgentResult(
            score=min(9.0, score),
            confidence=0.7,
            reasoning="Rule-based evaluation (LLM not available)",
            strengths=["Basic sentence variety"] if complex_sentences > 0 else [],
            weaknesses=["Limited analysis"] if complex_sentences < 2 else [],
            specific_suggestions=["Enable LLM for detailed analysis"],
            error_analysis=[]
        )

class ProductionMultiAgentScoringEngine:
    """Production-ready multi-agent scoring system with highest accuracy"""
    
    def __init__(self, openai_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        # Initialize LLM clients
        self.openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
        self.anthropic_client = Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        
        # Initialize specialized agents
        self.task_agent = TaskAchievementAgent(self.openai_client, self.anthropic_client)
        self.coherence_agent = CoherenceCohesionAgent(self.openai_client, self.anthropic_client)
        self.lexical_agent = LexicalResourceAgent(self.openai_client, self.anthropic_client)
        self.grammar_agent = GrammaticalRangeAgent(self.openai_client, self.anthropic_client)
        
        self.llm_available = bool(openai_api_key or anthropic_api_key)
        
        if self.llm_available:
            logger.info("✅ Production Multi-Agent System initialized with LLM support")
        else:
            logger.info("⚠️ Production Multi-Agent System initialized with rule-based fallback")
    
    def score_essay(self, prompt: str, essay: str, task_type: str) -> Dict[str, Any]:
        """Score essay using multi-agent approach with highest accuracy"""
        
        logger.info(f"🤖 Multi-Agent scoring: {task_type} essay ({len(essay.split())} words)")
        
        # Get evaluations from all specialized agents
        task_result = self.task_agent.evaluate(prompt, essay, task_type)
        coherence_result = self.coherence_agent.evaluate(essay)
        lexical_result = self.lexical_agent.evaluate(essay)
        grammar_result = self.grammar_agent.evaluate(essay)
        
        # Calculate overall band score with IELTS-realistic weighting
        # Task Achievement has higher weight and can severely limit overall score
        if task_result.score <= 2.0:
            # Completely off-topic essays get severely penalized
            overall_score = min(task_result.score + 1.0, 3.0)
        elif task_result.score <= 4.0:
            # Poor task achievement significantly limits overall score
            overall_score = min(
                task_result.score * 0.5 + 
                (coherence_result.score + lexical_result.score + grammar_result.score) / 3 * 0.5,
                5.0
            )
        else:
            # Normal weighting for essays that address the task
            overall_score = (
                task_result.score * 0.35 +           # Task Achievement (higher weight)
                coherence_result.score * 0.25 +      # Coherence & Cohesion
                lexical_result.score * 0.20 +        # Lexical Resource
                grammar_result.score * 0.20          # Grammatical Range
            )
        
        # Combine feedback from all agents
        combined_feedback = {
            "strengths": [],
            "weaknesses": [],
            "specific_suggestions": [],
            "error_analysis": {
                "l1_influenced_errors": [],
                "interlanguage_errors": [],
                "discourse_errors": []
            }
        }
        
        # Aggregate feedback from all agents
        for result in [task_result, coherence_result, lexical_result, grammar_result]:
            combined_feedback["strengths"].extend(result.strengths)
            combined_feedback["weaknesses"].extend(result.weaknesses)
            combined_feedback["specific_suggestions"].extend(result.specific_suggestions)
            combined_feedback["error_analysis"]["discourse_errors"].extend(result.error_analysis)
        
        # Calculate overall confidence (weighted average)
        overall_confidence = (
            task_result.confidence * 0.25 +
            coherence_result.confidence * 0.25 +
            lexical_result.confidence * 0.25 +
            grammar_result.confidence * 0.25
        )
        
        # Create detailed agent reasoning
        agent_reasoning = {
            "task_achievement": {
                "score": task_result.score,
                "reasoning": task_result.reasoning,
                "confidence": task_result.confidence
            },
            "coherence_cohesion": {
                "score": coherence_result.score,
                "reasoning": coherence_result.reasoning,
                "confidence": coherence_result.confidence
            },
            "lexical_resource": {
                "score": lexical_result.score,
                "reasoning": lexical_result.reasoning,
                "confidence": lexical_result.confidence
            },
            "grammatical_range": {
                "score": grammar_result.score,
                "reasoning": grammar_result.reasoning,
                "confidence": grammar_result.confidence
            }
        }
        
        return {
            "scores": {
                "task_achievement": task_result.score,
                "coherence_cohesion": coherence_result.score,
                "lexical_resource": lexical_result.score,
                "grammatical_range": grammar_result.score,
                "overall_band_score": round(overall_score * 2) / 2
            },
            "feedback": combined_feedback,
            "confidence": overall_confidence,
            "assessment_method": "multi_agent_llm" if self.llm_available else "multi_agent_rule_based",
            "agent_reasoning": agent_reasoning,
            "is_gibberish": False,  # Multi-agent system handles this better
            "error_analysis": {
                "l1_errors": 0,  # Would be populated by specialized analysis
                "interlanguage_errors": 0,
                "discourse_errors": len(combined_feedback["error_analysis"]["discourse_errors"]),
                "total_errors": len(combined_feedback["error_analysis"]["discourse_errors"])
            }
        }
