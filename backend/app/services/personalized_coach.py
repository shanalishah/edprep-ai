"""
Personalized Coach AI Service
AI-powered personal tutoring and coaching system
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import openai
from anthropic import Anthropic
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class CoachingStyle(str, Enum):
    ENCOURAGING = "encouraging"
    ANALYTICAL = "analytical"
    MOTIVATIONAL = "motivational"
    DETAILED = "detailed"
    CONCISE = "concise"

class LearningPreference(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"
    MIXED = "mixed"

class CoachPersonality(BaseModel):
    name: str
    style: CoachingStyle
    tone: str
    expertise_areas: List[str]
    motivational_approach: str
    feedback_style: str

class CoachingSession(BaseModel):
    session_id: str
    user_id: str
    topic: str
    duration_minutes: int
    coach_personality: CoachPersonality
    content: str
    feedback: str
    recommendations: List[str]
    next_steps: List[str]
    created_at: datetime

class PersonalizedAdvice(BaseModel):
    advice_type: str
    title: str
    content: str
    priority: str  # "high", "medium", "low"
    actionable: bool
    estimated_impact: str
    time_required: str
    difficulty_level: str

class CoachingRequest(BaseModel):
    user_id: str
    topic: str
    current_level: float
    target_level: float
    weak_areas: List[str]
    strong_areas: List[str]
    learning_preference: LearningPreference
    coaching_style: CoachingStyle
    specific_questions: List[str] = []
    context: str = ""

class CoachingResponse(BaseModel):
    session: CoachingSession
    personalized_advice: List[PersonalizedAdvice]
    study_plan_adjustments: List[str]
    motivation_message: str
    processing_time: float
    confidence: float

class PersonalizedCoachAI:
    """AI-powered personalized coaching system"""
    
    def __init__(self, openai_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        self.openai_client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None
        self.anthropic_client = Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        self.is_available = bool(openai_api_key or anthropic_api_key)
        
        # Coach personalities
        self.coach_personalities = {
            CoachingStyle.ENCOURAGING: CoachPersonality(
                name="Sarah",
                style=CoachingStyle.ENCOURAGING,
                tone="warm and supportive",
                expertise_areas=["motivation", "confidence building", "positive reinforcement"],
                motivational_approach="focuses on strengths and celebrates small wins",
                feedback_style="constructive and uplifting"
            ),
            CoachingStyle.ANALYTICAL: CoachPersonality(
                name="Dr. Chen",
                style=CoachingStyle.ANALYTICAL,
                tone="precise and data-driven",
                expertise_areas=["performance analysis", "skill assessment", "strategic planning"],
                motivational_approach="uses data and metrics to drive improvement",
                feedback_style="detailed and evidence-based"
            ),
            CoachingStyle.MOTIVATIONAL: CoachPersonality(
                name="Coach Mike",
                style=CoachingStyle.MOTIVATIONAL,
                tone="energetic and inspiring",
                expertise_areas=["goal setting", "persistence", "overcoming challenges"],
                motivational_approach="inspires through stories and challenges",
                feedback_style="energetic and goal-oriented"
            ),
            CoachingStyle.DETAILED: CoachPersonality(
                name="Professor Williams",
                style=CoachingStyle.DETAILED,
                tone="thorough and comprehensive",
                expertise_areas=["deep learning", "skill mastery", "advanced techniques"],
                motivational_approach="focuses on mastery and deep understanding",
                feedback_style="comprehensive and detailed"
            ),
            CoachingStyle.CONCISE: CoachPersonality(
                name="Alex",
                style=CoachingStyle.CONCISE,
                tone="direct and efficient",
                expertise_areas=["quick wins", "efficiency", "time management"],
                motivational_approach="focuses on practical, actionable steps",
                feedback_style="clear and to-the-point"
            )
        }
        
        # Learning preference adaptations
        self.learning_adaptations = {
            LearningPreference.VISUAL: {
                "content_format": "diagrams, charts, and visual examples",
                "study_methods": ["mind maps", "infographics", "video tutorials"],
                "feedback_style": "visual progress indicators and charts"
            },
            LearningPreference.AUDITORY: {
                "content_format": "spoken explanations and audio examples",
                "study_methods": ["podcasts", "audio recordings", "discussions"],
                "feedback_style": "verbal feedback and audio explanations"
            },
            LearningPreference.KINESTHETIC: {
                "content_format": "hands-on activities and practical exercises",
                "study_methods": ["writing practice", "role-playing", "interactive exercises"],
                "feedback_style": "practical demonstrations and exercises"
            },
            LearningPreference.READING_WRITING: {
                "content_format": "written materials and text-based examples",
                "study_methods": ["reading guides", "written exercises", "note-taking"],
                "feedback_style": "detailed written feedback and corrections"
            },
            LearningPreference.MIXED: {
                "content_format": "varied formats combining multiple approaches",
                "study_methods": ["multimedia content", "varied exercises", "flexible approaches"],
                "feedback_style": "diverse feedback methods"
            }
        }
        
        if not self.is_available:
            logger.warning("⚠️ No LLM API keys provided, Personalized Coach will use template-based responses")
    
    async def provide_coaching(self, request: CoachingRequest) -> CoachingResponse:
        """Provide personalized AI coaching session"""
        
        try:
            # Select appropriate coach personality
            coach_personality = self.coach_personalities[request.coaching_style]
            
            # Generate coaching content
            if self.is_available:
                coaching_content = await self._generate_ai_coaching(request, coach_personality)
            else:
                coaching_content = self._generate_template_coaching(request, coach_personality)
            
            # Generate personalized advice
            personalized_advice = await self._generate_personalized_advice(request, coach_personality)
            
            # Generate study plan adjustments
            study_plan_adjustments = self._generate_study_plan_adjustments(request)
            
            # Generate motivation message
            motivation_message = self._generate_motivation_message(request, coach_personality)
            
            # Create coaching session
            session = CoachingSession(
                session_id=f"coaching_{request.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                user_id=request.user_id,
                topic=request.topic,
                duration_minutes=30,
                coach_personality=coach_personality,
                content=coaching_content["content"],
                feedback=coaching_content["feedback"],
                recommendations=coaching_content["recommendations"],
                next_steps=coaching_content["next_steps"],
                created_at=datetime.now()
            )
            
            return CoachingResponse(
                session=session,
                personalized_advice=personalized_advice,
                study_plan_adjustments=study_plan_adjustments,
                motivation_message=motivation_message,
                processing_time=0.0,  # Will be set by caller
                confidence=0.8 if self.is_available else 0.6
            )
            
        except Exception as e:
            logger.error(f"❌ Personalized coaching failed: {e}")
            raise e
    
    async def _generate_ai_coaching(self, request: CoachingRequest, coach: CoachPersonality) -> Dict[str, Any]:
        """Generate AI-powered coaching content"""
        
        learning_adaptation = self.learning_adaptations[request.learning_preference]
        
        prompt = f"""
        You are {coach.name}, an expert IELTS coach with a {coach.tone} personality.
        
        Student Profile:
        - Current Level: {request.current_level}
        - Target Level: {request.target_level}
        - Weak Areas: {', '.join(request.weak_areas)}
        - Strong Areas: {', '.join(request.strong_areas)}
        - Learning Preference: {request.learning_preference.value}
        - Topic: {request.topic}
        - Specific Questions: {', '.join(request.specific_questions)}
        - Context: {request.context}
        
        Your coaching style: {coach.feedback_style}
        Your expertise: {', '.join(coach.expertise_areas)}
        Your motivational approach: {coach.motivational_approach}
        
        Learning adaptation for {request.learning_preference.value} learners:
        - Content format: {learning_adaptation['content_format']}
        - Study methods: {', '.join(learning_adaptation['study_methods'])}
        - Feedback style: {learning_adaptation['feedback_style']}
        
        Provide a comprehensive coaching session including:
        1. Personalized content addressing their specific needs
        2. Detailed feedback on their current performance
        3. Specific recommendations for improvement
        4. Clear next steps for their learning journey
        
        Format as JSON:
        {{
            "content": "Detailed coaching content tailored to the student",
            "feedback": "Specific feedback on their performance and areas for improvement",
            "recommendations": ["Recommendation 1", "Recommendation 2", "Recommendation 3"],
            "next_steps": ["Next step 1", "Next step 2", "Next step 3"]
        }}
        """
        
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=2000
                )
                result_text = response.choices[0].message.content
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2000,
                    temperature=0.3,
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
                result = self._generate_template_coaching(request, coach)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ AI coaching generation failed: {e}")
            return self._generate_template_coaching(request, coach)
    
    def _generate_template_coaching(self, request: CoachingRequest, coach: CoachPersonality) -> Dict[str, Any]:
        """Generate template-based coaching when AI is not available"""
        
        content = f"""
        Hello! I'm {coach.name}, your personalized IELTS coach. I'm here to help you improve your {request.topic} skills.
        
        Based on your current level of {request.current_level} and target of {request.target_level}, I can see you have some great strengths in {', '.join(request.strong_areas)} and areas to focus on in {', '.join(request.weak_areas)}.
        
        As a {request.learning_preference.value} learner, I'll adapt my coaching to your preferred learning style.
        """
        
        feedback = f"""
        Your current performance shows promise in {', '.join(request.strong_areas)}. 
        To reach your target level of {request.target_level}, focus on improving {', '.join(request.weak_areas)}.
        """
        
        recommendations = [
            f"Practice {area} exercises daily" for area in request.weak_areas[:2]
        ]
        recommendations.extend([
            "Review your mistakes and learn from them",
            "Set specific, measurable goals for each week"
        ])
        
        next_steps = [
            "Complete the recommended practice exercises",
            "Schedule regular practice sessions",
            "Track your progress weekly"
        ]
        
        return {
            "content": content,
            "feedback": feedback,
            "recommendations": recommendations,
            "next_steps": next_steps
        }
    
    async def _generate_personalized_advice(self, request: CoachingRequest, coach: CoachPersonality) -> List[PersonalizedAdvice]:
        """Generate personalized advice based on student profile"""
        
        advice_list = []
        
        # Advice 1: Weak area focus
        if request.weak_areas:
            advice_list.append(PersonalizedAdvice(
                advice_type="weak_area_focus",
                title=f"Focus on {request.weak_areas[0].replace('_', ' ').title()}",
                content=f"Your {request.weak_areas[0]} needs the most attention. Practice specific exercises targeting this area.",
                priority="high",
                actionable=True,
                estimated_impact="Significant improvement in 2-3 weeks",
                time_required="30 minutes daily",
                difficulty_level="intermediate"
            ))
        
        # Advice 2: Learning preference adaptation
        learning_adaptation = self.learning_adaptations[request.learning_preference]
        advice_list.append(PersonalizedAdvice(
            advice_type="learning_adaptation",
            title=f"Optimize for {request.learning_preference.value.title()} Learning",
            content=f"Use {learning_adaptation['content_format']} to maximize your learning efficiency.",
            priority="medium",
            actionable=True,
            estimated_impact="Improved retention and understanding",
            time_required="No additional time",
            difficulty_level="easy"
        ))
        
        # Advice 3: Goal achievement strategy
        score_gap = request.target_level - request.current_level
        if score_gap > 1.0:
            advice_list.append(PersonalizedAdvice(
                advice_type="goal_strategy",
                title="Strategic Goal Achievement",
                content=f"With a {score_gap:.1f} point gap, focus on incremental improvements and consistent practice.",
                priority="high",
                actionable=True,
                estimated_impact="Reach target in 6-8 weeks",
                time_required="1 hour daily",
                difficulty_level="intermediate"
            ))
        
        # Advice 4: Strength building
        if request.strong_areas:
            advice_list.append(PersonalizedAdvice(
                advice_type="strength_building",
                title=f"Leverage Your {request.strong_areas[0].replace('_', ' ').title()} Strength",
                content=f"Use your strong {request.strong_areas[0]} skills to support improvement in other areas.",
                priority="medium",
                actionable=True,
                estimated_impact="Faster overall improvement",
                time_required="15 minutes daily",
                difficulty_level="easy"
            ))
        
        return advice_list[:5]  # Limit to 5 pieces of advice
    
    def _generate_study_plan_adjustments(self, request: CoachingRequest) -> List[str]:
        """Generate study plan adjustments based on coaching session"""
        
        adjustments = []
        
        # Adjust for weak areas
        for area in request.weak_areas[:2]:
            adjustments.append(f"Increase practice time for {area.replace('_', ' ')} by 20%")
        
        # Adjust for learning preference
        learning_adaptation = self.learning_adaptations[request.learning_preference]
        adjustments.append(f"Incorporate more {learning_adaptation['study_methods'][0]} into your study routine")
        
        # Adjust for goal timeline
        score_gap = request.target_level - request.current_level
        if score_gap > 1.5:
            adjustments.append("Increase daily study time to 90 minutes")
        elif score_gap < 0.5:
            adjustments.append("Focus on maintaining consistency rather than increasing intensity")
        
        # General adjustments
        adjustments.extend([
            "Add weekly progress reviews",
            "Include more practice tests in your routine"
        ])
        
        return adjustments[:5]  # Limit to 5 adjustments
    
    def _generate_motivation_message(self, request: CoachingRequest, coach: CoachPersonality) -> str:
        """Generate personalized motivation message"""
        
        score_gap = request.target_level - request.current_level
        
        if coach.style == CoachingStyle.ENCOURAGING:
            return f"You're doing great! With your strong {', '.join(request.strong_areas)} skills, you're well on your way to achieving your {request.target_level} target. Keep up the excellent work!"
        
        elif coach.style == CoachingStyle.MOTIVATIONAL:
            return f"Every expert was once a beginner. Your journey from {request.current_level} to {request.target_level} is achievable with dedication and the right strategy. Let's make it happen!"
        
        elif coach.style == CoachingStyle.ANALYTICAL:
            return f"Based on your current trajectory and the {score_gap:.1f} point gap to your target, you're positioned for success. Focus on the data-driven improvements we've identified."
        
        elif coach.style == CoachingStyle.DETAILED:
            return f"Mastery comes through deliberate practice. Your detailed approach to improving {', '.join(request.weak_areas)} will yield significant results. Stay committed to the process."
        
        else:  # CONCISE
            return f"Target: {request.target_level}. Current: {request.current_level}. Gap: {score_gap:.1f}. Action: Focus on {request.weak_areas[0] if request.weak_areas else 'overall improvement'}. Result: Success."
    
    async def get_coach_recommendation(self, user_id: str, user_preferences: Dict[str, Any]) -> CoachPersonality:
        """Recommend the best coach personality for a user"""
        
        # Analyze user preferences to recommend coach
        if user_preferences.get("needs_encouragement", False):
            return self.coach_personalities[CoachingStyle.ENCOURAGING]
        elif user_preferences.get("likes_data", False):
            return self.coach_personalities[CoachingStyle.ANALYTICAL]
        elif user_preferences.get("needs_motivation", False):
            return self.coach_personalities[CoachingStyle.MOTIVATIONAL]
        elif user_preferences.get("wants_detail", False):
            return self.coach_personalities[CoachingStyle.DETAILED]
        else:
            return self.coach_personalities[CoachingStyle.CONCISE]
    
    def get_available_coaches(self) -> List[CoachPersonality]:
        """Get all available coach personalities"""
        return list(self.coach_personalities.values())
    
    def get_coaching_styles(self) -> List[str]:
        """Get available coaching styles"""
        return [style.value for style in CoachingStyle]
    
    def get_learning_preferences(self) -> List[str]:
        """Get available learning preferences"""
        return [pref.value for pref in LearningPreference]
    
    def get_coaching_features(self) -> List[str]:
        """Get available coaching features"""
        return [
            "Personalized AI coaching sessions",
            "Adaptive learning style support",
            "Multiple coach personalities",
            "Real-time feedback and advice",
            "Study plan optimization",
            "Progress-based recommendations",
            "Motivational messaging",
            "Weak area identification",
            "Strength leveraging",
            "Goal achievement strategies"
        ]


