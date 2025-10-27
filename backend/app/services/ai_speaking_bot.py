import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import openai
from anthropic import Anthropic
import os

logger = logging.getLogger(__name__)

class IELTSSpeakingBot:
    """
    AI-powered IELTS Speaking Test Bot that conducts tests like a real human examiner.
    Provides voice-to-voice conversation with realistic IELTS test environment.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        self.openai_client = None
        self.anthropic_client = None
        self.current_test_session = None
        self.conversation_history = []
        
        # Initialize AI clients with API keys passed as parameters or from environment
        openai_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        anthropic_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        
        # Debug logging
        logger.info(f"🔍 Debug - OpenAI key available: {bool(openai_key and openai_key != 'your-openai-api-key-here')}")
        logger.info(f"🔍 Debug - Anthropic key available: {bool(anthropic_key and anthropic_key != 'your-anthropic-api-key-here')}")
        
        if openai_key and openai_key != "your-openai-api-key-here":
            try:
                self.openai_client = openai.AsyncOpenAI(api_key=openai_key)
                logger.info("✅ OpenAI client initialized for speaking bot")
            except Exception as e:
                logger.warning(f"⚠️ OpenAI client not available: {e}")
        else:
            logger.warning("⚠️ OpenAI API key not provided for speaking bot")
        
        if anthropic_key and anthropic_key != "your-anthropic-api-key-here":
            try:
                self.anthropic_client = Anthropic(api_key=anthropic_key)
                logger.info("✅ Anthropic client initialized for speaking bot")
            except Exception as e:
                logger.warning(f"⚠️ Anthropic client not available: {e}")
        else:
            logger.warning("⚠️ Anthropic API key not provided for speaking bot")
    
    def set_ai_clients(self, openai_client, anthropic_client):
        """
        Set AI clients from external sources (e.g., from main app)
        """
        if openai_client:
            self.openai_client = openai_client
            logger.info("✅ OpenAI client set for speaking bot")
        if anthropic_client:
            self.anthropic_client = anthropic_client
            logger.info("✅ Anthropic client set for speaking bot")
    
    async def start_test_session(self, test_id: str, user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Start a new IELTS speaking test session with the AI bot.
        """
        try:
            # Load test data
            test_data = await self._load_test_data(test_id)
            
            # Initialize session
            self.current_test_session = {
                "test_id": test_id,
                "user_profile": user_profile or {},
                "test_data": test_data,
                "current_part": 1,
                "current_question": 0,
                "start_time": datetime.now(),
                "responses": [],
                "conversation_history": [],
                "bot_personality": self._get_examiner_personality()
            }
            
            # Generate welcome message
            welcome_message = await self._generate_welcome_message()
            
            return {
                "session_id": f"speaking_bot_{test_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "welcome_message": welcome_message,
                "test_info": {
                    "title": test_data.get("title", "IELTS Speaking Test"),
                    "total_parts": 3,
                    "estimated_duration": "11-14 minutes",
                    "current_part": 1
                },
                "bot_personality": self.current_test_session["bot_personality"]
            }
            
        except Exception as e:
            logger.error(f"❌ Error starting test session: {e}")
            raise
    
    async def process_user_response(self, user_audio_text: str, session_id: str) -> Dict[str, Any]:
        """
        Process user's spoken response and generate bot's next question/feedback.
        """
        try:
            if not self.current_test_session:
                raise ValueError("No active test session")
            
            # Add user response to conversation history
            self.current_test_session["conversation_history"].append({
                "role": "user",
                "content": user_audio_text,
                "timestamp": datetime.now()
            })
            
            # Analyze user response
            response_analysis = await self._analyze_user_response(user_audio_text)
            
            # Generate bot's next response
            bot_response = await self._generate_bot_response(user_audio_text, response_analysis)
            
            # Add bot response to conversation history
            self.current_test_session["conversation_history"].append({
                "role": "bot",
                "content": bot_response["text"],
                "timestamp": datetime.now()
            })
            
            # Update session state
            self._update_session_state(response_analysis, bot_response)
            
            return {
                "bot_response": bot_response,
                "session_state": {
                    "current_part": self.current_test_session["current_part"],
                    "current_question": self.current_test_session["current_question"],
                    "progress_percentage": self._calculate_progress(),
                    "time_elapsed": self._get_time_elapsed()
                },
                "response_analysis": response_analysis
            }
            
        except Exception as e:
            logger.error(f"❌ Error processing user response: {e}")
            raise
    
    async def complete_test(self, session_id: str) -> Dict[str, Any]:
        """
        Complete the test and generate comprehensive assessment.
        """
        try:
            if not self.current_test_session:
                raise ValueError("No active test session")
            
            # Generate final assessment
            final_assessment = await self._generate_final_assessment()
            
            # Generate closing message
            closing_message = await self._generate_closing_message(final_assessment)
            
            # Prepare results
            results = {
                "session_summary": {
                    "test_id": self.current_test_session["test_id"],
                    "duration": self._get_time_elapsed(),
                    "total_responses": len(self.current_test_session["responses"]),
                    "parts_completed": self.current_test_session["current_part"]
                },
                "assessment": final_assessment,
                "closing_message": closing_message,
                "detailed_feedback": await self._generate_detailed_feedback(),
                "improvement_suggestions": await self._generate_improvement_suggestions(final_assessment)
            }
            
            # Clear session
            self.current_test_session = None
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error completing test: {e}")
            raise
    
    def _get_examiner_personality(self) -> Dict[str, str]:
        """
        Define the AI examiner's personality and speaking style.
        """
        return {
            "name": "Sarah",
            "role": "IELTS Speaking Examiner",
            "personality": "Professional, encouraging, and supportive",
            "speaking_style": "Clear, measured, and friendly",
            "accent": "Neutral British English",
            "greeting_style": "Warm and professional",
            "question_style": "Natural conversation flow",
            "feedback_style": "Constructive and encouraging"
        }
    
    async def _generate_welcome_message(self) -> str:
        """
        Generate a welcoming message from the AI examiner.
        """
        personality = self.current_test_session["bot_personality"]
        
        welcome_prompt = f"""
        You are {personality['name']}, an IELTS Speaking Examiner with a {personality['personality']} personality.
        You are about to conduct an IELTS Speaking Test.
        
        Generate a warm, professional welcome message that:
        1. Greets the candidate warmly
        2. Introduces yourself briefly
        3. Explains what will happen in the test
        4. Sets a comfortable, professional tone
        5. Keeps it concise (2-3 sentences)
        
        Speak as if you're talking directly to the candidate in a natural, conversational way.
        """
        
        if self.openai_client:
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": welcome_prompt}],
                    max_tokens=150,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"OpenAI error: {e}")
        
        # Fallback message
        return f"Hello! I'm {personality['name']}, your IELTS Speaking Examiner today. I'll be conducting your speaking test, which will take about 11-14 minutes and consists of three parts. Don't worry, I'm here to help you do your best. Let's begin!"
    
    async def _generate_bot_response(self, user_response: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate the bot's next response based on user input and test progress.
        """
        personality = self.current_test_session["bot_personality"]
        current_part = self.current_test_session["current_part"]
        current_question = self.current_test_session["current_question"]
        test_data = self.current_test_session["test_data"]
        
        # Build conversation context
        conversation_context = self._build_conversation_context()
        
        # Get intelligent next question based on context
        next_question = await self._get_intelligent_next_question(user_response, analysis, conversation_context)
        
        # Create sophisticated AI prompt
        response_prompt = f"""
        You are {personality['name']}, a professional IELTS Speaking Examiner with {personality['personality']} personality.
        
        CONVERSATION CONTEXT:
        - Current Part: {current_part} of 3
        - Question Number: {current_question + 1}
        - Previous conversation: {conversation_context}
        
        CANDIDATE'S RESPONSE: "{user_response}"
        
        RESPONSE ANALYSIS:
        - Fluency Score: {analysis.get('fluency_score', 'N/A')}/9
        - Coherence Score: {analysis.get('coherence_score', 'N/A')}/9
        - Vocabulary Score: {analysis.get('lexical_resource_score', 'N/A')}/9
        - Grammar Score: {analysis.get('grammar_score', 'N/A')}/9
        - Overall Score: {analysis.get('overall_score', 'N/A')}/9
        - Strengths: {', '.join(analysis.get('strengths', []))}
        - Areas for improvement: {', '.join(analysis.get('areas_for_improvement', []))}
        
        YOUR TASK:
        Generate a natural, human-like response that:
        1. Acknowledges their response with specific details (show you're listening)
        2. Provides subtle encouragement based on their performance
        3. Smoothly transitions to the next question: "{next_question}"
        4. Maintains professional but warm examiner tone
        5. Adapts your language to their level (if they're struggling, be more supportive)
        6. Keeps the conversation flowing naturally
        
        EXAMINER PERSONALITY:
        - {personality['personality']}
        - {personality['speaking_style']}
        - Professional but approachable
        - Encouraging and supportive
        
        RESPONSE GUIDELINES:
        - Be conversational, not robotic
        - Show genuine interest in their answers
        - Use natural transitions
        - Keep responses concise (2-3 sentences max)
        - Don't repeat the question exactly - paraphrase naturally
        
        Generate your response now:
        """
        
        if self.openai_client:
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a professional IELTS Speaking Examiner conducting a real test. Be natural, encouraging, and human-like in your responses."},
                        {"role": "user", "content": response_prompt}
                    ],
                    max_tokens=250,
                    temperature=0.8
                )
                bot_text = response.choices[0].message.content.strip()
                logger.info(f"🤖 AI Generated Response: {bot_text[:100]}...")
            except Exception as e:
                logger.error(f"OpenAI error: {e}")
                bot_text = self._get_fallback_response(user_response, next_question, analysis)
        else:
            bot_text = self._get_fallback_response(user_response, next_question, analysis)
        
        return {
            "text": bot_text,
            "audio_url": None,  # Will be generated by text-to-speech
            "question_type": "follow_up" if current_question > 0 else "initial",
            "part": current_part,
            "question_number": current_question + 1
        }
    
    def _build_conversation_context(self) -> str:
        """
        Build conversation context from the session history.
        """
        if not self.current_test_session or not self.current_test_session.get("conversation_history"):
            return "Beginning of conversation"
        
        recent_messages = self.current_test_session["conversation_history"][-4:]  # Last 4 exchanges
        context_parts = []
        
        for msg in recent_messages:
            role = "Candidate" if msg["role"] == "user" else "Examiner"
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            context_parts.append(f"{role}: {content}")
        
        return " | ".join(context_parts)
    
    async def _get_intelligent_next_question(self, user_response: str, analysis: Dict[str, Any], context: str) -> str:
        """
        Generate intelligent next questions based on context and user performance.
        """
        current_part = self.current_test_session["current_part"]
        current_question = self.current_test_session["current_question"]
        
        if current_part == 1:
            # Part 1 questions - more personal and introductory
            questions = [
                "Do you work or are you a student?",
                "What do you like about your job/studies?",
                "What are your future plans?",
                "Do you enjoy meeting new people?",
                "What do you do in your free time?",
                "Tell me about your hometown.",
                "What's your favorite type of music?",
                "Do you prefer reading books or watching movies?"
            ]
            
            if current_question < len(questions):
                return questions[current_question]
            else:
                return "Now I'd like to give you a topic to talk about. You'll have one minute to prepare and then speak for up to two minutes."
        
        elif current_part == 2:
            # Part 2 - Individual long turn
            topics = [
                "Describe a person who has influenced you greatly",
                "Describe a memorable trip you've taken",
                "Describe a book you've read recently",
                "Describe a place you'd like to visit",
                "Describe a skill you'd like to learn"
            ]
            return f"I'd like you to {topics[current_question % len(topics)].lower()}. You have one minute to prepare and then speak for up to two minutes."
        
        else:
            # Part 3 - Two-way discussion
            discussion_questions = [
                "Let's discuss the importance of education in today's society.",
                "What do you think about the impact of technology on communication?",
                "How do you see the future of work changing?",
                "What role do you think governments should play in environmental protection?",
                "How important is it for people to learn foreign languages?"
            ]
            return discussion_questions[current_question % len(discussion_questions)]
    
    def _get_fallback_response(self, user_response: str, next_question: str, analysis: Dict[str, Any]) -> str:
        """
        Generate a fallback response when AI is not available.
        """
        personality = self.current_test_session["bot_personality"]
        
        # Simple acknowledgment based on response length
        if len(user_response.split()) < 10:
            return f"That's interesting. {next_question}"
        elif len(user_response.split()) < 30:
            return f"Thank you for sharing that. {next_question}"
        else:
            return f"I appreciate your detailed response. {next_question}"
    
    async def _analyze_user_response(self, user_response: str) -> Dict[str, Any]:
        """
        Analyze the user's response for fluency, coherence, vocabulary, and grammar.
        """
        current_part = self.current_test_session['current_part']
        conversation_context = self._build_conversation_context()
        
        analysis_prompt = f"""
        You are an expert IELTS Speaking Examiner analyzing a candidate's response.
        
        CONTEXT:
        - Part: {current_part} of 3
        - Conversation history: {conversation_context}
        - Candidate's response: "{user_response}"
        
        TASK:
        Provide a comprehensive analysis in JSON format. Be precise and professional.
        
        ANALYSIS CRITERIA:
        1. Fluency & Coherence (1-9): Natural flow, coherence, hesitation, self-correction
        2. Lexical Resource (1-9): Vocabulary range, accuracy, appropriateness
        3. Grammatical Range & Accuracy (1-9): Sentence variety, accuracy, complexity
        4. Pronunciation (1-9): Clarity, stress, intonation, accent
        
        RESPONSE FORMAT (JSON only):
        {{
            "fluency_score": 6.5,
            "coherence_score": 7.0,
            "lexical_resource_score": 6.0,
            "grammar_score": 6.5,
            "pronunciation_score": 7.0,
            "overall_score": 6.6,
            "strengths": ["Clear pronunciation", "Good vocabulary range", "Coherent ideas"],
            "areas_for_improvement": ["Reduce hesitation", "Improve grammar accuracy", "Expand vocabulary"],
            "response_length": "appropriate",
            "topic_relevance": "high",
            "confidence_level": "medium",
            "detailed_feedback": "The candidate demonstrates good pronunciation and coherent ideas. However, there are some grammatical errors and hesitations that affect fluency."
        }}
        
        IMPORTANT: Return ONLY valid JSON. No additional text.
        """
        
        if self.openai_client:
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an expert IELTS Speaking Examiner. Provide precise, professional analysis in JSON format only."},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    max_tokens=400,
                    temperature=0.2
                )
                analysis_text = response.choices[0].message.content.strip()
                
                # Clean and extract JSON
                analysis_text = analysis_text.replace('```json', '').replace('```', '').strip()
                
                try:
                    analysis = json.loads(analysis_text)
                    logger.info(f"📊 AI Analysis: Overall {analysis.get('overall_score', 'N/A')}/9")
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing error: {e}")
                    logger.error(f"Raw response: {analysis_text}")
                    analysis = self._get_fallback_analysis(user_response)
                
            except Exception as e:
                logger.error(f"OpenAI analysis error: {e}")
                analysis = self._get_fallback_analysis(user_response)
        else:
            logger.warning("⚠️ OpenAI client not available, using fallback analysis")
            analysis = self._get_fallback_analysis(user_response)
        
        return analysis
    
    def _get_fallback_analysis(self, user_response: str) -> Dict[str, Any]:
        """
        Provide fallback analysis when AI services are unavailable.
        """
        word_count = len(user_response.split())
        
        # Basic scoring based on response length and content
        if word_count < 10:
            fluency_score = 3.0
            coherence_score = 3.0
        elif word_count < 30:
            fluency_score = 5.0
            coherence_score = 5.0
        else:
            fluency_score = 6.5
            coherence_score = 6.5
        
        return {
            "fluency_score": fluency_score,
            "coherence_score": coherence_score,
            "lexical_resource_score": 5.5,
            "grammar_score": 5.5,
            "pronunciation_score": 5.5,
            "overall_score": (fluency_score + coherence_score + 5.5 + 5.5 + 5.5) / 5,
            "strengths": ["Clear communication", "Good response length"],
            "areas_for_improvement": ["Expand vocabulary", "Improve grammar accuracy"],
            "response_length": "appropriate" if 10 <= word_count <= 100 else "short" if word_count < 10 else "long",
            "topic_relevance": "high",
            "confidence_level": "medium"
        }
    
    async def _generate_final_assessment(self) -> Dict[str, Any]:
        """
        Generate comprehensive final assessment based on all responses.
        """
        if not self.current_test_session["responses"]:
            return self._get_default_assessment()
        
        # Calculate average scores
        all_scores = [resp.get("analysis", {}) for resp in self.current_test_session["responses"]]
        
        avg_fluency = sum(score.get("fluency_score", 5.0) for score in all_scores) / len(all_scores)
        avg_coherence = sum(score.get("coherence_score", 5.0) for score in all_scores) / len(all_scores)
        avg_lexical = sum(score.get("lexical_resource_score", 5.0) for score in all_scores) / len(all_scores)
        avg_grammar = sum(score.get("grammar_score", 5.0) for score in all_scores) / len(all_scores)
        avg_pronunciation = sum(score.get("pronunciation_score", 5.0) for score in all_scores) / len(all_scores)
        
        overall_score = (avg_fluency + avg_coherence + avg_lexical + avg_grammar + avg_pronunciation) / 5
        
        return {
            "overall_score": round(overall_score, 1),
            "fluency_score": round(avg_fluency, 1),
            "coherence_score": round(avg_coherence, 1),
            "lexical_resource_score": round(avg_lexical, 1),
            "grammar_score": round(avg_grammar, 1),
            "pronunciation_score": round(avg_pronunciation, 1),
            "band_level": self._get_band_level(overall_score),
            "total_responses": len(self.current_test_session["responses"]),
            "test_duration": self._get_time_elapsed()
        }
    
    def _get_band_level(self, score: float) -> str:
        """
        Convert numerical score to IELTS band level.
        """
        if score >= 8.5:
            return "Band 9 (Expert User)"
        elif score >= 8.0:
            return "Band 8 (Very Good User)"
        elif score >= 7.0:
            return "Band 7 (Good User)"
        elif score >= 6.0:
            return "Band 6 (Competent User)"
        elif score >= 5.0:
            return "Band 5 (Modest User)"
        elif score >= 4.0:
            return "Band 4 (Limited User)"
        elif score >= 3.0:
            return "Band 3 (Extremely Limited User)"
        else:
            return "Band 2 (Intermittent User)"
    
    async def _generate_closing_message(self, assessment: Dict[str, Any]) -> str:
        """
        Generate a closing message from the examiner.
        """
        personality = self.current_test_session["bot_personality"]
        band_level = assessment["band_level"]
        
        return f"Thank you for completing the IELTS Speaking Test. You've demonstrated {band_level} level English proficiency. Your overall performance shows good communication skills with room for continued improvement. Keep practicing, and you'll continue to develop your English speaking abilities. Good luck with your future studies!"
    
    async def _generate_detailed_feedback(self) -> List[Dict[str, str]]:
        """
        Generate detailed feedback for each part of the test.
        """
        feedback = []
        
        for i, response in enumerate(self.current_test_session["responses"]):
            analysis = response.get("analysis", {})
            feedback.append({
                "part": f"Response {i+1}",
                "score": analysis.get("overall_score", 5.0),
                "strengths": ", ".join(analysis.get("strengths", [])),
                "improvements": ", ".join(analysis.get("areas_for_improvement", []))
            })
        
        return feedback
    
    async def _generate_improvement_suggestions(self, assessment: Dict[str, Any]) -> List[str]:
        """
        Generate personalized improvement suggestions.
        """
        suggestions = []
        
        if assessment["fluency_score"] < 6.0:
            suggestions.append("Practice speaking more fluently by reducing pauses and hesitations")
        
        if assessment["lexical_resource_score"] < 6.0:
            suggestions.append("Expand your vocabulary by learning more advanced words and phrases")
        
        if assessment["grammar_score"] < 6.0:
            suggestions.append("Focus on improving grammar accuracy, especially verb tenses and sentence structure")
        
        if assessment["pronunciation_score"] < 6.0:
            suggestions.append("Work on pronunciation clarity and stress patterns")
        
        if not suggestions:
            suggestions.append("Continue practicing to maintain and improve your current level")
        
        return suggestions
    
    def _update_session_state(self, analysis: Dict[str, Any], bot_response: Dict[str, Any]):
        """
        Update the current session state based on user response and bot response.
        """
        # Add response to session
        self.current_test_session["responses"].append({
            "response": analysis,
            "timestamp": datetime.now(),
            "analysis": analysis
        })
        
        # Update question counter
        self.current_test_session["current_question"] += 1
        
        # Check if we need to move to next part
        test_data = self.current_test_session["test_data"]
        questions = test_data.get("questions", [])
        
        if self.current_test_session["current_part"] == 1 and self.current_test_session["current_question"] >= len(questions):
            self.current_test_session["current_part"] = 2
            self.current_test_session["current_question"] = 0
        elif self.current_test_session["current_part"] == 2 and self.current_test_session["current_question"] >= 1:
            self.current_test_session["current_part"] = 3
            self.current_test_session["current_question"] = 0
    
    def _calculate_progress(self) -> int:
        """
        Calculate test progress percentage.
        """
        if not self.current_test_session:
            return 0
        
        total_parts = 3
        current_part = self.current_test_session["current_part"]
        
        if current_part == 1:
            questions = self.current_test_session["test_data"].get("questions", [])
            progress = (self.current_test_session["current_question"] / len(questions)) * 33
        elif current_part == 2:
            progress = 33 + (self.current_test_session["current_question"] * 33)
        else:
            progress = 66 + (self.current_test_session["current_question"] * 33)
        
        return min(100, int(progress))
    
    def _get_time_elapsed(self) -> str:
        """
        Get formatted time elapsed since test start.
        """
        if not self.current_test_session:
            return "0:00"
        
        elapsed = datetime.now() - self.current_test_session["start_time"]
        minutes = int(elapsed.total_seconds() // 60)
        seconds = int(elapsed.total_seconds() % 60)
        return f"{minutes}:{seconds:02d}"
    
    async def _load_test_data(self, test_id: str) -> Dict[str, Any]:
        """
        Load test data for the given test ID.
        """
        # This would typically load from database or file
        # For now, return sample data
        return {
            "id": test_id,
            "title": "IELTS Speaking Test",
            "questions": [
                {"instruction": "Do you work or are you a student?"},
                {"instruction": "What do you like about your job/studies?"},
                {"instruction": "What are your future plans?"},
                {"instruction": "Do you enjoy meeting new people?"},
                {"instruction": "What do you do in your free time?"}
            ]
        }
    
    def _get_default_assessment(self) -> Dict[str, Any]:
        """
        Return default assessment when no responses are available.
        """
        return {
            "overall_score": 1.0,
            "fluency_score": 1.0,
            "coherence_score": 1.0,
            "lexical_resource_score": 1.0,
            "grammar_score": 1.0,
            "pronunciation_score": 1.0,
            "band_level": "Band 1 (Non-User)",
            "total_responses": 0,
            "test_duration": "0:00"
        }

# Global instance
# Create global instance with API keys
import os
ai_speaking_bot = IELTSSpeakingBot(
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    anthropic_api_key=os.getenv('ANTHROPIC_API_KEY')
)
