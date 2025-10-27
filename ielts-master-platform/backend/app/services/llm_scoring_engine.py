"""
LLM-Powered Essay Scoring Engine
Uses modern LLMs for sophisticated essay analysis and scoring
"""

import json
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI
from anthropic import Anthropic
import re

logger = logging.getLogger(__name__)

class LLMScoringEngine:
    """Advanced LLM-powered essay scoring engine"""
    
    def __init__(self, openai_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        self.openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
        self.anthropic_client = Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        self.is_available = bool(openai_api_key or anthropic_api_key)
        
        if not self.is_available:
            logger.warning("⚠️ No LLM API keys provided, LLM scoring unavailable")
    
    def score_essay_with_llm(self, prompt: str, essay: str, task_type: str) -> Dict[str, Any]:
        """Score essay using LLM with structured output"""
        
        if not self.is_available:
            raise ValueError("LLM scoring not available - no API keys provided")
        
        # Create detailed scoring prompt
        scoring_prompt = self._create_scoring_prompt(prompt, essay, task_type)
        
        try:
            if self.openai_client:
                return self._score_with_openai(scoring_prompt, essay)
            elif self.anthropic_client:
                return self._score_with_anthropic(scoring_prompt, essay)
        except Exception as e:
            logger.error(f"❌ LLM scoring failed: {e}")
            raise
    
    def _create_scoring_prompt(self, prompt: str, essay: str, task_type: str) -> str:
        """Create detailed scoring prompt for LLM"""
        
        return f"""
You are an expert IELTS Writing examiner. Please evaluate this essay according to the official IELTS Writing Task {task_type[-1]} criteria.

**Task Prompt:** {prompt}

**Essay to Evaluate:**
{essay}

**Evaluation Criteria:**

1. **Task Achievement (Task 2) / Task Response (Task 1):**
   - How well does the essay address the task?
   - Is the position clear and consistent?
   - Are main ideas supported with relevant examples?
   - Is the conclusion appropriate?

2. **Coherence and Cohesion:**
   - Is the essay well-organized with clear paragraphs?
   - Are ideas logically connected?
   - Are linking words and cohesive devices used effectively?
   - Is there a clear progression of ideas?

3. **Lexical Resource:**
   - Is vocabulary appropriate and varied?
   - Are words used accurately and precisely?
   - Is there evidence of less common vocabulary?
   - Are collocations natural?

4. **Grammatical Range and Accuracy:**
   - Is there a variety of sentence structures?
   - Are complex sentences used accurately?
   - Is grammar generally accurate?
   - Do errors impede communication?

**Scoring Scale:** 1.0 to 9.0 (in 0.5 increments)

Please provide your evaluation in the following JSON format:
{{
    "task_achievement": <score>,
    "coherence_cohesion": <score>,
    "lexical_resource": <score>,
    "grammatical_range": <score>,
    "overall_band_score": <score>,
    "detailed_feedback": {{
        "strengths": ["strength1", "strength2", ...],
        "weaknesses": ["weakness1", "weakness2", ...],
        "specific_suggestions": ["suggestion1", "suggestion2", ...],
        "error_analysis": {{
            "l1_influenced_errors": ["error1", "error2", ...],
            "interlanguage_errors": ["error1", "error2", ...],
            "discourse_errors": ["error1", "error2", ...]
        }}
    }},
    "confidence": <0.0-1.0>,
    "reasoning": "Brief explanation of the scoring rationale"
}}
"""
    
    def _score_with_openai(self, prompt: str, essay: str) -> Dict[str, Any]:
        """Score using OpenAI GPT-4 with function calling"""
        
        # Define the function schema for structured output
        function_schema = {
            "name": "score_essay",
            "description": "Score an IELTS essay according to official criteria",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_achievement": {
                        "type": "number",
                        "description": "Task Achievement score (1.0-9.0)",
                        "minimum": 1.0,
                        "maximum": 9.0
                    },
                    "coherence_cohesion": {
                        "type": "number", 
                        "description": "Coherence and Cohesion score (1.0-9.0)",
                        "minimum": 1.0,
                        "maximum": 9.0
                    },
                    "lexical_resource": {
                        "type": "number",
                        "description": "Lexical Resource score (1.0-9.0)", 
                        "minimum": 1.0,
                        "maximum": 9.0
                    },
                    "grammatical_range": {
                        "type": "number",
                        "description": "Grammatical Range and Accuracy score (1.0-9.0)",
                        "minimum": 1.0,
                        "maximum": 9.0
                    },
                    "overall_band_score": {
                        "type": "number",
                        "description": "Overall Band Score (1.0-9.0)",
                        "minimum": 1.0,
                        "maximum": 9.0
                    },
                    "detailed_feedback": {
                        "type": "object",
                        "properties": {
                            "strengths": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "weaknesses": {
                                "type": "array", 
                                "items": {"type": "string"}
                            },
                            "specific_suggestions": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "error_analysis": {
                                "type": "object",
                                "properties": {
                                    "l1_influenced_errors": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "interlanguage_errors": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "discourse_errors": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence in the scoring (0.0-1.0)",
                        "minimum": 0.0,
                        "maximum": 1.0
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Brief explanation of scoring rationale"
                    }
                },
                "required": ["task_achievement", "coherence_cohesion", "lexical_resource", "grammatical_range", "overall_band_score", "detailed_feedback", "confidence", "reasoning"]
            }
        }
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert IELTS Writing examiner with extensive experience in evaluating essays according to official IELTS criteria."},
                    {"role": "user", "content": prompt}
                ],
                functions=[function_schema],
                function_call={"name": "score_essay"},
                temperature=0.1,  # Low temperature for consistent scoring
                max_tokens=2000
            )
            
            # Extract the function call result
            function_call = response.choices[0].message.function_call
            if function_call and function_call.name == "score_essay":
                result = json.loads(function_call.arguments)
                
                # Round scores to nearest 0.5
                for key in ["task_achievement", "coherence_cohesion", "lexical_resource", "grammatical_range", "overall_band_score"]:
                    if key in result:
                        result[key] = round(result[key] * 2) / 2
                
                return {
                    "scores": {
                        "task_achievement": result["task_achievement"],
                        "coherence_cohesion": result["coherence_cohesion"], 
                        "lexical_resource": result["lexical_resource"],
                        "grammatical_range": result["grammatical_range"],
                        "overall_band_score": result["overall_band_score"]
                    },
                    "feedback": result["detailed_feedback"],
                    "confidence": result["confidence"],
                    "reasoning": result["reasoning"],
                    "assessment_method": "llm_gpt4"
                }
            else:
                raise ValueError("No function call in response")
                
        except Exception as e:
            logger.error(f"❌ OpenAI API error: {e}")
            raise
    
    def _score_with_anthropic(self, prompt: str, essay: str) -> Dict[str, Any]:
        """Score using Anthropic Claude with structured output"""
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse the JSON response
            content = response.content[0].text
            result = json.loads(content)
            
            # Round scores to nearest 0.5
            for key in ["task_achievement", "coherence_cohesion", "lexical_resource", "grammatical_range", "overall_band_score"]:
                if key in result:
                    result[key] = round(result[key] * 2) / 2
            
            return {
                "scores": {
                    "task_achievement": result["task_achievement"],
                    "coherence_cohesion": result["coherence_cohesion"],
                    "lexical_resource": result["lexical_resource"], 
                    "grammatical_range": result["grammatical_range"],
                    "overall_band_score": result["overall_band_score"]
                },
                "feedback": result["detailed_feedback"],
                "confidence": result["confidence"],
                "reasoning": result["reasoning"],
                "assessment_method": "llm_claude"
            }
            
        except Exception as e:
            logger.error(f"❌ Anthropic API error: {e}")
            raise
    
    def generate_enhanced_feedback(self, essay: str, scores: Dict[str, float], prompt: str) -> str:
        """Generate detailed, personalized feedback using LLM"""
        
        feedback_prompt = f"""
Based on the following essay and scores, provide detailed, actionable feedback to help the student improve:

**Task Prompt:** {prompt}
**Essay:** {essay}
**Scores:**
- Task Achievement: {scores.get('task_achievement', 'N/A')}
- Coherence & Cohesion: {scores.get('coherence_cohesion', 'N/A')}
- Lexical Resource: {scores.get('lexical_resource', 'N/A')}
- Grammatical Range: {scores.get('grammatical_range', 'N/A')}
- Overall Band Score: {scores.get('overall_band_score', 'N/A')}

Please provide:
1. Specific strengths to build upon
2. Key areas for improvement with examples
3. Actionable suggestions for each criterion
4. Common error patterns and how to avoid them
5. Next steps for improvement

Make the feedback encouraging but honest, specific but not overwhelming.
"""
        
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are a supportive IELTS Writing tutor who provides detailed, actionable feedback to help students improve their writing skills."},
                        {"role": "user", "content": feedback_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1500
                )
                return response.choices[0].message.content
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1500,
                    temperature=0.3,
                    messages=[
                        {"role": "user", "content": feedback_prompt}
                    ]
                )
                return response.content[0].text
        except Exception as e:
            logger.error(f"❌ Error generating enhanced feedback: {e}")
            return "Unable to generate detailed feedback at this time."
