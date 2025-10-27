"""
Advanced AI Feedback Generator for IELTS Writing Assessment
Provides sophisticated feedback with L1, interlanguage, and discourse analysis
"""

import os
import re
from typing import Dict, List, Any, Optional
import logging
from openai import OpenAI
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class AdvancedAIFeedbackGenerator:
    """
    Advanced AI feedback generator with sophisticated error analysis
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        self.openai_client = None
        self.anthropic_client = None
        
        if openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=openai_api_key)
                logger.info("✅ OpenAI client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI client: {e}")
        
        if anthropic_api_key:
            try:
                self.anthropic_client = Anthropic(api_key=anthropic_api_key)
                logger.info("✅ Anthropic client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Anthropic client: {e}")
    
    def generate_comprehensive_feedback(
        self, 
        prompt: str, 
        essay: str, 
        scores: Dict[str, float], 
        error_analysis: Dict[str, int],
        task_type: str = "Task 2"
    ) -> Dict[str, Any]:
        """Generate comprehensive feedback with AI analysis"""
        
        try:
            # Generate AI feedback if available
            if self.openai_client or self.anthropic_client:
                ai_feedback = self._generate_ai_feedback(prompt, essay, scores, error_analysis, task_type)
            else:
                ai_feedback = self._generate_rule_based_feedback(prompt, essay, scores, error_analysis, task_type)
            
            # Generate specific suggestions
            suggestions = self._generate_suggestions(essay, scores, error_analysis)
            
            # Generate improvement plan
            improvement_plan = self._generate_improvement_plan(scores, error_analysis)
            
            # Generate strengths and weaknesses
            strengths_weaknesses = self._analyze_strengths_weaknesses(essay, scores, error_analysis)
            
            return {
                "detailed_feedback": ai_feedback,
                "suggestions": suggestions,
                "improvement_plan": improvement_plan,
                "strengths_weaknesses": strengths_weaknesses,
                "error_analysis": error_analysis,
                "feedback_type": "ai_generated" if (self.openai_client or self.anthropic_client) else "rule_based"
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating feedback: {e}")
            return self._generate_fallback_feedback(scores, error_analysis)
    
    def _generate_ai_feedback(
        self, 
        prompt: str, 
        essay: str, 
        scores: Dict[str, float], 
        error_analysis: Dict[str, int],
        task_type: str
    ) -> str:
        """Generate AI-powered feedback using OpenAI or Anthropic"""
        
        # Create detailed prompt for AI
        ai_prompt = self._create_ai_prompt(prompt, essay, scores, error_analysis, task_type)
        
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert IELTS writing examiner with deep knowledge of language learning theory, L1 interference, interlanguage development, and discourse analysis. Provide detailed, constructive feedback that helps students improve their writing skills."
                        },
                        {
                            "role": "user",
                            "content": ai_prompt
                        }
                    ],
                    max_tokens=1500,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1500,
                    temperature=0.7,
                    system="You are an expert IELTS writing examiner with deep knowledge of language learning theory, L1 interference, interlanguage development, and discourse analysis. Provide detailed, constructive feedback that helps students improve their writing skills.",
                    messages=[
                        {
                            "role": "user",
                            "content": ai_prompt
                        }
                    ]
                )
                return response.content[0].text.strip()
        
        except Exception as e:
            logger.error(f"❌ AI feedback generation failed: {e}")
            return self._generate_rule_based_feedback(prompt, essay, scores, error_analysis, task_type)
    
    def _create_ai_prompt(
        self, 
        prompt: str, 
        essay: str, 
        scores: Dict[str, float], 
        error_analysis: Dict[str, int],
        task_type: str
    ) -> str:
        """Create detailed prompt for AI feedback generation"""
        
        return f"""
Please provide comprehensive feedback for this IELTS {task_type} essay:

**Writing Prompt:**
{prompt}

**Student's Essay:**
{essay}

**Scores:**
- Task Achievement: {scores.get('task_achievement', 0)}/9
- Coherence & Cohesion: {scores.get('coherence_cohesion', 0)}/9
- Lexical Resource: {scores.get('lexical_resource', 0)}/9
- Grammatical Range & Accuracy: {scores.get('grammatical_range', 0)}/9
- Overall Band Score: {scores.get('overall_band_score', 0)}/9

**Error Analysis:**
- L1-influenced errors: {error_analysis.get('l1_errors', 0)}
- Interlanguage errors: {error_analysis.get('interlanguage_errors', 0)}
- Discourse management errors: {error_analysis.get('discourse_errors', 0)}
- Total errors: {error_analysis.get('total_errors', 0)}

**Please provide feedback covering:**

1. **Overall Assessment** - Brief summary of performance
2. **Task Achievement** - How well the essay addresses the prompt
3. **Coherence & Cohesion** - Organization and linking
4. **Lexical Resource** - Vocabulary range and accuracy
5. **Grammatical Range & Accuracy** - Grammar variety and correctness

**Focus on:**
- Specific examples from the essay
- L1 interference patterns if present
- Interlanguage development issues
- Discourse management problems
- Actionable improvement suggestions
- Positive reinforcement for strengths

**Tone:** Professional, encouraging, and constructive. Use specific examples from the essay to illustrate points.
"""
    
    def _generate_rule_based_feedback(
        self, 
        prompt: str, 
        essay: str, 
        scores: Dict[str, float], 
        error_analysis: Dict[str, int],
        task_type: str
    ) -> str:
        """Generate rule-based feedback as fallback"""
        
        feedback_parts = []
        
        # Overall assessment
        overall_score = scores.get('overall_band_score', 0)
        if overall_score >= 7.0:
            feedback_parts.append("**Overall Assessment:** Excellent work! Your essay demonstrates strong writing skills with clear organization and effective language use.")
        elif overall_score >= 6.0:
            feedback_parts.append("**Overall Assessment:** Good work! Your essay shows solid writing skills with room for improvement in specific areas.")
        elif overall_score >= 5.0:
            feedback_parts.append("**Overall Assessment:** Your essay shows basic competence but needs significant improvement in several areas.")
        else:
            feedback_parts.append("**Overall Assessment:** Your essay needs substantial improvement to meet IELTS standards.")
        
        # Task Achievement feedback
        ta_score = scores.get('task_achievement', 0)
        if ta_score < 6.0:
            feedback_parts.append(f"""
**Task Achievement ({ta_score}/9):** Your essay doesn't fully address the task requirements. Make sure to:
- Clearly state your position in the introduction
- Develop your arguments with specific examples
- Write at least 250 words for Task 2
- Include a clear conclusion that summarizes your main points
""")
        
        # Coherence & Cohesion feedback
        cc_score = scores.get('coherence_cohesion', 0)
        if cc_score < 6.0:
            feedback_parts.append(f"""
**Coherence and Cohesion ({cc_score}/9):** Improve the organization and flow of your essay:
- Use clear paragraph structure (introduction, body paragraphs, conclusion)
- Add linking words like 'however', 'therefore', 'moreover', 'furthermore'
- Start each paragraph with a clear topic sentence
""")
        
        # Lexical Resource feedback
        lr_score = scores.get('lexical_resource', 0)
        if lr_score < 6.0:
            feedback_parts.append(f"""
**Lexical Resource ({lr_score}/9):** Expand your vocabulary:
- Use more varied and precise vocabulary
- Avoid repeating the same words
- Include some academic vocabulary appropriate for the topic
- Check word choice for accuracy
""")
        
        # Grammatical Range feedback
        gr_score = scores.get('grammatical_range', 0)
        if gr_score < 6.0:
            feedback_parts.append(f"""
**Grammatical Range and Accuracy ({gr_score}/9):** Improve your grammar:
- Use a variety of sentence structures (simple, compound, complex)
- Check subject-verb agreement
- Use correct verb tenses consistently
- Proofread for spelling and punctuation errors
""")
        
        # Error analysis feedback
        if error_analysis.get('l1_errors', 0) > 0:
            feedback_parts.append(f"""
**L1 Influence:** You have {error_analysis['l1_errors']} errors that may be influenced by your first language. Try to:
- Use more natural English expressions
- Avoid direct translations from your native language
- Practice with native English materials
""")
        
        if error_analysis.get('interlanguage_errors', 0) > 0:
            feedback_parts.append(f"""
**Interlanguage Development:** You have {error_analysis['interlanguage_errors']} interlanguage errors. Focus on:
- Learning common English collocations
- Understanding article usage
- Practicing preposition combinations
""")
        
        if error_analysis.get('discourse_errors', 0) > 0:
            feedback_parts.append(f"""
**Discourse Management:** You have {error_analysis['discourse_errors']} discourse management issues. Work on:
- Using appropriate linking words
- Avoiding contradictory connectors
- Making clear references with pronouns
""")
        
        return "\n\n".join(feedback_parts)
    
    def _generate_suggestions(self, essay: str, scores: Dict[str, float], error_analysis: Dict[str, int]) -> List[str]:
        """Generate specific improvement suggestions"""
        
        suggestions = []
        
        # CRITICAL: Task Achievement issues take priority
        task_achievement_score = scores.get('task_achievement', 0)
        if task_achievement_score <= 2.0:
            suggestions.append("🚨 CRITICAL: Your essay is completely off-topic! You must address the exact question asked in the prompt.")
            suggestions.append("Read the prompt carefully and ensure every sentence relates to the topic.")
            suggestions.append("Practice identifying key words in the prompt and staying focused on the specific question.")
            return suggestions[:5]  # Return immediately for off-topic essays
        
        # Word count suggestions
        word_count = len(essay.split())
        if word_count < 250:
            suggestions.append(f"Write more! Your essay has {word_count} words. Aim for at least 250 words for Task 2.")
        
        # Task Achievement suggestions (for essays that are on-topic but incomplete)
        if task_achievement_score < 6.0 and task_achievement_score > 2.0:
            suggestions.append("Make sure you fully address all parts of the task question.")
            suggestions.append("Develop your arguments with specific examples and explanations.")
            suggestions.append("Include a clear introduction, body paragraphs, and conclusion.")
        
        # Grammar suggestions
        if scores.get('grammatical_range', 0) < 6.0:
            suggestions.append("Practice using complex sentences with conjunctions like 'because', 'although', 'while'.")
            suggestions.append("Review common grammar rules, especially subject-verb agreement and verb tenses.")
        
        # Vocabulary suggestions
        if scores.get('lexical_resource', 0) < 6.0:
            suggestions.append("Learn 5-10 new academic words each day and practice using them in sentences.")
            suggestions.append("Use a thesaurus to find synonyms for common words you use frequently.")
        
        # Coherence suggestions
        if scores.get('coherence_cohesion', 0) < 6.0:
            suggestions.append("Practice using linking words to connect your ideas more effectively.")
            suggestions.append("Make sure each paragraph has a clear topic sentence.")
        
        # Error-specific suggestions
        if error_analysis.get('l1_errors', 0) > 0:
            suggestions.append("Read more English texts to develop natural English expressions.")
        
        if error_analysis.get('interlanguage_errors', 0) > 0:
            suggestions.append("Study common English collocations and preposition combinations.")
        
        if error_analysis.get('discourse_errors', 0) > 0:
            suggestions.append("Practice using pronouns and linking words to improve text cohesion.")
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _generate_improvement_plan(self, scores: Dict[str, float], error_analysis: Dict[str, int]) -> Dict[str, Any]:
        """Generate personalized improvement plan"""
        
        plan = {
            "immediate_focus": [],
            "short_term_goals": [],
            "long_term_goals": [],
            "recommended_resources": []
        }
        
        # CRITICAL: Off-topic essays get immediate attention
        task_achievement_score = scores.get('task_achievement', 0)
        if task_achievement_score <= 2.0:
            plan["immediate_focus"].append("🚨 CRITICAL: Learn to read and understand essay prompts correctly")
            plan["immediate_focus"].append("Practice identifying the exact question being asked")
            plan["short_term_goals"].append("Write 10 practice essays focusing ONLY on staying on-topic")
            plan["short_term_goals"].append("Practice prompt analysis - identify key words and requirements")
            plan["recommended_resources"].append("IELTS Task 2 prompt analysis exercises")
            return plan
        
        # Identify weakest areas
        weakest_criterion = min(scores.items(), key=lambda x: x[1])
        
        if weakest_criterion[0] == "task_achievement":
            plan["immediate_focus"].append("Practice addressing the task requirements completely")
            plan["short_term_goals"].append("Write 5 practice essays focusing on task response")
        elif weakest_criterion[0] == "coherence_cohesion":
            plan["immediate_focus"].append("Improve essay organization and linking")
            plan["short_term_goals"].append("Practice using linking words and paragraph structure")
        elif weakest_criterion[0] == "lexical_resource":
            plan["immediate_focus"].append("Expand vocabulary range and accuracy")
            plan["short_term_goals"].append("Learn 20 new academic words per week")
        elif weakest_criterion[0] == "grammatical_range":
            plan["immediate_focus"].append("Improve grammar variety and accuracy")
            plan["short_term_goals"].append("Practice complex sentence structures")
        
        # Error-specific plans
        if error_analysis.get('l1_errors', 0) > 5:
            plan["immediate_focus"].append("Reduce L1 interference in writing")
            plan["recommended_resources"].append("Native English writing samples")
        
        if error_analysis.get('interlanguage_errors', 0) > 5:
            plan["immediate_focus"].append("Study English collocations and prepositions")
            plan["recommended_resources"].append("Collocation dictionaries and grammar books")
        
        # Long-term goals
        overall_score = scores.get('overall_band_score', 0)
        if overall_score < 6.0:
            plan["long_term_goals"].append("Achieve Band 6.0 overall score")
        elif overall_score < 7.0:
            plan["long_term_goals"].append("Achieve Band 7.0 overall score")
        else:
            plan["long_term_goals"].append("Maintain current high performance")
        
        return plan
    
    def _analyze_strengths_weaknesses(self, essay: str, scores: Dict[str, float], error_analysis: Dict[str, int]) -> Dict[str, List[str]]:
        """Analyze strengths and weaknesses"""
        
        strengths = []
        weaknesses = []
        
        # Analyze strengths
        if scores.get('overall_band_score', 0) >= 7.0:
            strengths.append("Strong overall writing performance")
        
        if scores.get('task_achievement', 0) >= 7.0:
            strengths.append("Excellent task response and argument development")
        
        if scores.get('coherence_cohesion', 0) >= 7.0:
            strengths.append("Well-organized essay with effective linking")
        
        if scores.get('lexical_resource', 0) >= 7.0:
            strengths.append("Rich vocabulary and accurate word choice")
        
        if scores.get('grammatical_range', 0) >= 7.0:
            strengths.append("Varied and accurate grammar structures")
        
        # Analyze weaknesses
        if scores.get('task_achievement', 0) < 6.0:
            weaknesses.append("Incomplete task response")
        
        if scores.get('coherence_cohesion', 0) < 6.0:
            weaknesses.append("Poor organization and weak linking")
        
        if scores.get('lexical_resource', 0) < 6.0:
            weaknesses.append("Limited vocabulary range")
        
        if scores.get('grammatical_range', 0) < 6.0:
            weaknesses.append("Limited grammar variety and accuracy issues")
        
        if error_analysis.get('l1_errors', 0) > 3:
            weaknesses.append("L1 interference affecting natural expression")
        
        if error_analysis.get('interlanguage_errors', 0) > 3:
            weaknesses.append("Interlanguage errors in grammar and collocations")
        
        if error_analysis.get('discourse_errors', 0) > 3:
            weaknesses.append("Discourse management issues")
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses
        }
    
    def _generate_fallback_feedback(self, scores: Dict[str, float], error_analysis: Dict[str, int]) -> Dict[str, Any]:
        """Generate basic fallback feedback"""
        
        return {
            "detailed_feedback": "Feedback generation failed. Please try again.",
            "suggestions": ["Review your essay for grammar and vocabulary errors."],
            "improvement_plan": {
                "immediate_focus": ["Practice writing more essays"],
                "short_term_goals": ["Improve overall writing skills"],
                "long_term_goals": ["Achieve target IELTS score"],
                "recommended_resources": ["IELTS writing practice books"]
            },
            "strengths_weaknesses": {
                "strengths": ["Attempted the task"],
                "weaknesses": ["Needs improvement in all areas"]
            },
            "error_analysis": error_analysis,
            "feedback_type": "fallback"
        }
