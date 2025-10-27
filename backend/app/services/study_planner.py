"""
AI-Powered Study Plans Service
Creates personalized study plans based on user performance and goals
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import openai
from anthropic import Anthropic
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class StudyPlanType(str, Enum):
    INTENSIVE = "intensive"  # 2-4 weeks
    STANDARD = "standard"    # 6-8 weeks
    EXTENDED = "extended"   # 10-12 weeks
    MAINTENANCE = "maintenance"  # Ongoing practice

class SkillLevel(str, Enum):
    BEGINNER = "beginner"      # Band 4-5
    INTERMEDIATE = "intermediate"  # Band 5.5-6.5
    ADVANCED = "advanced"      # Band 7-8
    EXPERT = "expert"          # Band 8.5-9

class StudySession(BaseModel):
    session_id: str
    title: str
    description: str
    duration_minutes: int
    difficulty_level: str
    skills_focused: List[str]
    resources: List[str]
    exercises: List[str]
    expected_outcome: str
    prerequisites: List[str]

class StudyPlan(BaseModel):
    plan_id: str
    user_id: str
    plan_type: StudyPlanType
    target_band_score: float
    current_band_score: float
    duration_weeks: int
    start_date: datetime
    end_date: datetime
    sessions: List[StudySession]
    milestones: List[Dict[str, Any]]
    progress_tracking: Dict[str, Any]
    adaptive_adjustments: List[Dict[str, Any]]

class StudyPlanRequest(BaseModel):
    user_id: str
    current_band_score: float
    target_band_score: float
    available_hours_per_week: int
    plan_type: StudyPlanType
    weak_areas: List[str]
    strong_areas: List[str]
    preferred_learning_style: str = "mixed"
    exam_date: Optional[datetime] = None

class StudyPlanResponse(BaseModel):
    study_plan: StudyPlan
    recommendations: List[str]
    success_probability: float
    estimated_improvement: float
    key_focus_areas: List[str]

class AIStudyPlanner:
    """AI-powered study plan generator"""
    
    def __init__(self, openai_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        self.openai_client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None
        self.anthropic_client = Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        self.is_available = bool(openai_api_key or anthropic_api_key)
        
        # IELTS skill areas
        self.skill_areas = {
            "writing": {
                "task_achievement": "Task Achievement and Response",
                "coherence_cohesion": "Coherence and Cohesion",
                "lexical_resource": "Lexical Resource",
                "grammatical_range": "Grammatical Range and Accuracy"
            },
            "reading": {
                "comprehension": "Reading Comprehension",
                "vocabulary": "Vocabulary in Context",
                "inference": "Inference and Analysis",
                "speed": "Reading Speed and Efficiency"
            },
            "listening": {
                "comprehension": "Listening Comprehension",
                "note_taking": "Note-taking Skills",
                "prediction": "Prediction and Anticipation",
                "focus": "Focus and Concentration"
            },
            "speaking": {
                "fluency": "Fluency and Coherence",
                "vocabulary": "Lexical Resource",
                "grammar": "Grammatical Range and Accuracy",
                "pronunciation": "Pronunciation"
            }
        }
        
        # Study plan templates
        self.plan_templates = {
            StudyPlanType.INTENSIVE: {
                "duration_weeks": 3,
                "sessions_per_week": 6,
                "session_duration": 90,
                "focus": "rapid_improvement"
            },
            StudyPlanType.STANDARD: {
                "duration_weeks": 7,
                "sessions_per_week": 4,
                "session_duration": 120,
                "focus": "balanced_development"
            },
            StudyPlanType.EXTENDED: {
                "duration_weeks": 11,
                "sessions_per_week": 3,
                "session_duration": 90,
                "focus": "comprehensive_preparation"
            },
            StudyPlanType.MAINTENANCE: {
                "duration_weeks": 4,
                "sessions_per_week": 2,
                "session_duration": 60,
                "focus": "skill_maintenance"
            }
        }
        
        if not self.is_available:
            logger.warning("⚠️ No LLM API keys provided, Study Planner will use template-based fallback")
    
    async def create_study_plan(self, request: StudyPlanRequest) -> StudyPlanResponse:
        """Create a personalized AI-powered study plan"""
        
        if not self.is_available:
            return self._template_based_plan(request)
        
        try:
            # Generate AI-powered study plan
            ai_plan = await self._generate_ai_plan(request)
            
            # Enhance with template-based structure
            enhanced_plan = self._enhance_with_templates(ai_plan, request)
            
            # Calculate success metrics
            success_metrics = self._calculate_success_metrics(enhanced_plan, request)
            
            return StudyPlanResponse(
                study_plan=enhanced_plan,
                recommendations=success_metrics["recommendations"],
                success_probability=success_metrics["success_probability"],
                estimated_improvement=success_metrics["estimated_improvement"],
                key_focus_areas=success_metrics["key_focus_areas"]
            )
            
        except Exception as e:
            logger.error(f"❌ AI study plan generation failed: {e}")
            return self._template_based_plan(request)
    
    async def _generate_ai_plan(self, request: StudyPlanRequest) -> StudyPlan:
        """Generate study plan using AI"""
        
        prompt = f"""
        You are an expert IELTS tutor. Create a personalized study plan for a student with the following profile:

        Current Band Score: {request.current_band_score}
        Target Band Score: {request.target_band_score}
        Available Hours per Week: {request.available_hours_per_week}
        Plan Type: {request.plan_type.value}
        Weak Areas: {', '.join(request.weak_areas)}
        Strong Areas: {', '.join(request.strong_areas)}
        Learning Style: {request.preferred_learning_style}
        Exam Date: {request.exam_date}

        Create a comprehensive study plan with:
        1. Weekly structure with specific sessions
        2. Focus areas based on weak points
        3. Progressive difficulty increase
        4. Milestones and checkpoints
        5. Specific exercises and resources
        6. Adaptive adjustments based on progress

        Format as JSON with this structure:
        {{
            "plan_id": "plan_123",
            "user_id": "{request.user_id}",
            "plan_type": "{request.plan_type.value}",
            "target_band_score": {request.target_band_score},
            "current_band_score": {request.current_band_score},
            "duration_weeks": 7,
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-02-19T00:00:00Z",
            "sessions": [
                {{
                    "session_id": "session_1",
                    "title": "Introduction to Task 2 Writing",
                    "description": "Learn the basics of IELTS Task 2 essay writing",
                    "duration_minutes": 90,
                    "difficulty_level": "beginner",
                    "skills_focused": ["task_achievement", "coherence_cohesion"],
                    "resources": ["IELTS Writing Guide", "Sample Essays"],
                    "exercises": ["Essay Structure Practice", "Topic Analysis"],
                    "expected_outcome": "Understand Task 2 requirements",
                    "prerequisites": []
                }}
            ],
            "milestones": [
                {{
                    "week": 2,
                    "description": "Complete basic essay structure",
                    "target_score": 5.5
                }}
            ],
            "progress_tracking": {{
                "weekly_assessments": true,
                "skill_tracking": ["writing", "reading", "listening", "speaking"],
                "adaptive_adjustments": true
            }},
            "adaptive_adjustments": []
        }}
        """
        
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=3000
                )
                result_text = response.choices[0].message.content
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=3000,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
                )
                result_text = response.content[0].text
            else:
                raise Exception("No AI client available")
            
            # Parse AI response
            import json
            try:
                plan_data = json.loads(result_text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                plan_data = self._parse_ai_plan_fallback(result_text, request)
            
            # Convert to StudyPlan object
            sessions = [StudySession(**session) for session in plan_data.get("sessions", [])]
            
            return StudyPlan(
                plan_id=plan_data.get("plan_id", f"plan_{request.user_id}_{datetime.now().strftime('%Y%m%d')}"),
                user_id=request.user_id,
                plan_type=StudyPlanType(plan_data.get("plan_type", request.plan_type.value)),
                target_band_score=plan_data.get("target_band_score", request.target_band_score),
                current_band_score=plan_data.get("current_band_score", request.current_band_score),
                duration_weeks=plan_data.get("duration_weeks", 7),
                start_date=datetime.fromisoformat(plan_data.get("start_date", datetime.now().isoformat())),
                end_date=datetime.fromisoformat(plan_data.get("end_date", (datetime.now() + timedelta(weeks=7)).isoformat())),
                sessions=sessions,
                milestones=plan_data.get("milestones", []),
                progress_tracking=plan_data.get("progress_tracking", {}),
                adaptive_adjustments=plan_data.get("adaptive_adjustments", [])
            )
            
        except Exception as e:
            logger.error(f"❌ AI plan generation failed: {e}")
            raise e
    
    def _enhance_with_templates(self, ai_plan: StudyPlan, request: StudyPlanRequest) -> StudyPlan:
        """Enhance AI plan with template-based structure"""
        
        template = self.plan_templates[ai_plan.plan_type]
        
        # Adjust session count based on available hours
        total_weekly_minutes = request.available_hours_per_week * 60
        template_sessions_per_week = template["sessions_per_week"]
        template_session_duration = template["session_duration"]
        
        # Calculate optimal session distribution
        if total_weekly_minutes < template_sessions_per_week * template_session_duration:
            # Reduce sessions or duration
            optimal_sessions = max(1, total_weekly_minutes // template_session_duration)
            optimal_duration = total_weekly_minutes // optimal_sessions
        else:
            optimal_sessions = template_sessions_per_week
            optimal_duration = template_session_duration
        
        # Update sessions with optimal timing
        for session in ai_plan.sessions:
            session.duration_minutes = optimal_duration
        
        return ai_plan
    
    def _calculate_success_metrics(self, plan: StudyPlan, request: StudyPlanRequest) -> Dict[str, Any]:
        """Calculate success probability and improvement estimates"""
        
        score_gap = request.target_band_score - request.current_band_score
        weeks_available = plan.duration_weeks
        
        # Success probability calculation
        if score_gap <= 0.5:
            success_probability = 0.95
        elif score_gap <= 1.0:
            success_probability = 0.85
        elif score_gap <= 1.5:
            success_probability = 0.70
        elif score_gap <= 2.0:
            success_probability = 0.50
        else:
            success_probability = 0.30
        
        # Adjust based on available time
        time_factor = min(1.0, request.available_hours_per_week / 10)
        success_probability *= time_factor
        
        # Estimated improvement
        estimated_improvement = min(score_gap, weeks_available * 0.3)
        
        # Key focus areas
        key_focus_areas = []
        for area in request.weak_areas:
            if area in ["writing", "reading", "listening", "speaking"]:
                key_focus_areas.extend(self.skill_areas.get(area, {}).keys())
        
        # Generate recommendations
        recommendations = []
        if success_probability < 0.7:
            recommendations.append("Consider extending your study timeline for better success probability")
        if request.available_hours_per_week < 5:
            recommendations.append("Increase study hours per week for optimal results")
        if len(request.weak_areas) > 3:
            recommendations.append("Focus on 2-3 key weak areas for maximum impact")
        
        return {
            "recommendations": recommendations,
            "success_probability": round(success_probability, 2),
            "estimated_improvement": round(estimated_improvement, 1),
            "key_focus_areas": list(set(key_focus_areas))
        }
    
    def _template_based_plan(self, request: StudyPlanRequest) -> StudyPlanResponse:
        """Create study plan using templates when AI is not available"""
        
        template = self.plan_templates[request.plan_type]
        
        # Create basic sessions
        sessions = []
        for week in range(template["duration_weeks"]):
            for session_num in range(template["sessions_per_week"]):
                session = StudySession(
                    session_id=f"session_{week}_{session_num}",
                    title=f"Week {week + 1} - Session {session_num + 1}",
                    description=f"Study session focusing on {request.weak_areas[0] if request.weak_areas else 'general IELTS skills'}",
                    duration_minutes=template["session_duration"],
                    difficulty_level="intermediate",
                    skills_focused=request.weak_areas[:2],
                    resources=["IELTS Practice Materials", "Sample Tests"],
                    exercises=["Practice Exercises", "Mock Tests"],
                    expected_outcome="Improved understanding and skills",
                    prerequisites=[]
                )
                sessions.append(session)
        
        # Create milestones
        milestones = []
        for week in range(2, template["duration_weeks"] + 1, 2):
            target_score = request.current_band_score + (week / template["duration_weeks"]) * (request.target_band_score - request.current_band_score)
            milestones.append({
                "week": week,
                "description": f"Week {week} assessment",
                "target_score": round(target_score, 1)
            })
        
        plan = StudyPlan(
            plan_id=f"template_plan_{request.user_id}_{datetime.now().strftime('%Y%m%d')}",
            user_id=request.user_id,
            plan_type=request.plan_type,
            target_band_score=request.target_band_score,
            current_band_score=request.current_band_score,
            duration_weeks=template["duration_weeks"],
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(weeks=template["duration_weeks"]),
            sessions=sessions,
            milestones=milestones,
            progress_tracking={
                "weekly_assessments": True,
                "skill_tracking": ["writing", "reading", "listening", "speaking"],
                "adaptive_adjustments": False
            },
            adaptive_adjustments=[]
        )
        
        success_metrics = self._calculate_success_metrics(plan, request)
        
        return StudyPlanResponse(
            study_plan=plan,
            recommendations=success_metrics["recommendations"],
            success_probability=success_metrics["success_probability"],
            estimated_improvement=success_metrics["estimated_improvement"],
            key_focus_areas=success_metrics["key_focus_areas"]
        )
    
    def _parse_ai_plan_fallback(self, ai_response: str, request: StudyPlanRequest) -> Dict[str, Any]:
        """Fallback parser for AI responses that aren't valid JSON"""
        
        # Extract basic information
        import re
        
        # Extract duration
        duration_match = re.search(r'duration[^:]*:\s*(\d+)', ai_response, re.IGNORECASE)
        duration_weeks = int(duration_match.group(1)) if duration_match else 7
        
        # Create basic plan structure
        return {
            "plan_id": f"ai_plan_{request.user_id}_{datetime.now().strftime('%Y%m%d')}",
            "user_id": request.user_id,
            "plan_type": request.plan_type.value,
            "target_band_score": request.target_band_score,
            "current_band_score": request.current_band_score,
            "duration_weeks": duration_weeks,
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(weeks=duration_weeks)).isoformat(),
            "sessions": [],
            "milestones": [],
            "progress_tracking": {},
            "adaptive_adjustments": []
        }
    
    def get_plan_types(self) -> List[str]:
        """Get available study plan types"""
        return [plan_type.value for plan_type in StudyPlanType]
    
    def get_skill_areas(self) -> Dict[str, Dict[str, str]]:
        """Get available skill areas"""
        return self.skill_areas


