"""
Progress Tracker AI Service
Intelligent progress tracking and learning analytics
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import statistics
from collections import defaultdict, Counter
import openai
from anthropic import Anthropic
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ProgressMetric(str, Enum):
    SCORE_IMPROVEMENT = "score_improvement"
    CONSISTENCY = "consistency"
    PRACTICE_FREQUENCY = "practice_frequency"
    SKILL_DEVELOPMENT = "skill_development"
    GOAL_ACHIEVEMENT = "goal_achievement"
    LEARNING_VELOCITY = "learning_velocity"

class LearningPattern(str, Enum):
    ACCELERATED = "accelerated"
    STEADY = "steady"
    PLATEAU = "plateau"
    DECLINING = "declining"
    IRREGULAR = "irregular"

class ProgressInsight(BaseModel):
    insight_type: str
    title: str
    description: str
    confidence: float
    impact_level: str  # "high", "medium", "low"
    actionable: bool
    recommendations: List[str]
    data_points: Dict[str, Any]

class LearningMilestone(BaseModel):
    milestone_id: str
    title: str
    description: str
    achieved_at: Optional[datetime]
    target_date: Optional[datetime]
    progress_percentage: float
    metrics: Dict[str, Any]

class ProgressReport(BaseModel):
    user_id: str
    period: str
    overall_progress: float
    learning_pattern: LearningPattern
    insights: List[ProgressInsight]
    milestones: List[LearningMilestone]
    predictions: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime

class ProgressTrackingRequest(BaseModel):
    user_id: str
    period_days: int = 30
    include_predictions: bool = True
    include_insights: bool = True
    focus_areas: List[str] = []

class ProgressTrackingResponse(BaseModel):
    report: ProgressReport
    processing_time: float
    confidence: float

class ProgressTrackerAI:
    """AI-powered progress tracking and learning analytics"""
    
    def __init__(self, openai_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        self.openai_client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None
        self.anthropic_client = Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        self.is_available = bool(openai_api_key or anthropic_api_key)
        
        # Sample progress data structure
        self.sample_progress_data = {
            "essay_scores": [
                {"date": "2024-01-01", "overall": 5.5, "task_achievement": 6.0, "coherence_cohesion": 5.0, "lexical_resource": 6.0, "grammatical_range": 5.0},
                {"date": "2024-01-08", "overall": 6.0, "task_achievement": 6.5, "coherence_cohesion": 5.5, "lexical_resource": 6.5, "grammatical_range": 5.5},
                {"date": "2024-01-15", "overall": 6.5, "task_achievement": 7.0, "coherence_cohesion": 6.0, "lexical_resource": 7.0, "grammatical_range": 6.0},
                {"date": "2024-01-22", "overall": 7.0, "task_achievement": 7.0, "coherence_cohesion": 7.0, "lexical_resource": 7.0, "grammatical_range": 7.0},
                {"date": "2024-01-29", "overall": 7.5, "task_achievement": 7.5, "coherence_cohesion": 7.5, "lexical_resource": 7.5, "grammatical_range": 7.5},
            ],
            "practice_sessions": [
                {"date": "2024-01-01", "duration_minutes": 60, "type": "writing", "difficulty": "intermediate"},
                {"date": "2024-01-02", "duration_minutes": 45, "type": "reading", "difficulty": "beginner"},
                {"date": "2024-01-03", "duration_minutes": 90, "type": "writing", "difficulty": "advanced"},
                {"date": "2024-01-04", "duration_minutes": 30, "type": "listening", "difficulty": "intermediate"},
                {"date": "2024-01-05", "duration_minutes": 75, "type": "speaking", "difficulty": "intermediate"},
            ],
            "goals": {
                "target_band_score": 8.0,
                "target_date": "2024-03-01",
                "current_band_score": 7.5
            },
            "weak_areas": ["coherence_cohesion", "grammatical_range"],
            "strong_areas": ["task_achievement", "lexical_resource"]
        }
        
        if not self.is_available:
            logger.warning("⚠️ No LLM API keys provided, Progress Tracker will use rule-based analysis")
    
    async def generate_progress_report(self, request: ProgressTrackingRequest) -> ProgressTrackingResponse:
        """Generate comprehensive progress tracking report"""
        
        try:
            # Get user progress data
            progress_data = self._get_progress_data(request.user_id, request.period_days)
            
            # Calculate overall progress
            overall_progress = self._calculate_overall_progress(progress_data)
            
            # Determine learning pattern
            learning_pattern = self._analyze_learning_pattern(progress_data)
            
            # Generate insights
            insights = []
            if request.include_insights:
                insights = await self._generate_progress_insights(progress_data, request.focus_areas)
            
            # Track milestones
            milestones = self._track_milestones(progress_data)
            
            # Generate predictions
            predictions = {}
            if request.include_predictions:
                predictions = await self._generate_predictions(progress_data, learning_pattern)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(insights, learning_pattern, progress_data)
            
            # Create progress report
            report = ProgressReport(
                user_id=request.user_id,
                period=f"{request.period_days} days",
                overall_progress=overall_progress,
                learning_pattern=learning_pattern,
                insights=insights,
                milestones=milestones,
                predictions=predictions,
                recommendations=recommendations,
                generated_at=datetime.now()
            )
            
            return ProgressTrackingResponse(
                report=report,
                processing_time=0.0,  # Will be set by caller
                confidence=0.8 if self.is_available else 0.6
            )
            
        except Exception as e:
            logger.error(f"❌ Progress tracking failed: {e}")
            raise e
    
    def _get_progress_data(self, user_id: str, period_days: int) -> Dict[str, Any]:
        """Get user's progress data for the specified period"""
        
        # In real implementation, this would query the database
        # For now, return sample data
        return self.sample_progress_data
    
    def _calculate_overall_progress(self, data: Dict[str, Any]) -> float:
        """Calculate overall progress percentage"""
        
        goals = data.get("goals", {})
        current_score = goals.get("current_band_score", 0.0)
        target_score = goals.get("target_band_score", 9.0)
        
        if target_score <= current_score:
            return 100.0
        
        # Calculate progress based on score improvement
        essay_scores = data.get("essay_scores", [])
        if len(essay_scores) >= 2:
            first_score = essay_scores[0]["overall"]
            last_score = essay_scores[-1]["overall"]
            improvement = last_score - first_score
            target_improvement = target_score - first_score
            
            if target_improvement > 0:
                progress = (improvement / target_improvement) * 100
                return min(100.0, max(0.0, progress))
        
        return 0.0
    
    def _analyze_learning_pattern(self, data: Dict[str, Any]) -> LearningPattern:
        """Analyze learning pattern from progress data"""
        
        essay_scores = data.get("essay_scores", [])
        if len(essay_scores) < 3:
            return LearningPattern.IRREGULAR
        
        scores = [score["overall"] for score in essay_scores]
        
        # Calculate trend
        if len(scores) >= 3:
            # Simple linear trend analysis
            first_half = scores[:len(scores)//2]
            second_half = scores[len(scores)//2:]
            
            first_avg = statistics.mean(first_half)
            second_avg = statistics.mean(second_half)
            
            improvement_rate = second_avg - first_avg
            
            if improvement_rate > 0.5:
                return LearningPattern.ACCELERATED
            elif improvement_rate > 0.1:
                return LearningPattern.STEADY
            elif improvement_rate < -0.1:
                return LearningPattern.DECLINING
            else:
                return LearningPattern.PLATEAU
        
        return LearningPattern.IRREGULAR
    
    async def _generate_progress_insights(self, data: Dict[str, Any], focus_areas: List[str]) -> List[ProgressInsight]:
        """Generate AI-powered progress insights"""
        
        if not self.is_available:
            return self._rule_based_insights(data)
        
        try:
            # Prepare data for AI analysis
            analysis_data = self._prepare_analysis_data(data)
            
            prompt = f"""
            You are an expert IELTS learning analyst. Analyze the following student progress data and generate insights.

            Progress Data:
            {analysis_data}

            Focus Areas: {focus_areas if focus_areas else "All areas"}

            Generate 3-5 key insights including:
            1. Performance trends and patterns
            2. Strengths and areas for improvement
            3. Learning velocity and consistency
            4. Goal achievement progress
            5. Specific recommendations

            Format as JSON:
            {{
                "insights": [
                    {{
                        "insight_type": "performance_trend",
                        "title": "Rapid Improvement Detected",
                        "description": "Your writing scores have improved significantly over the past month",
                        "confidence": 0.9,
                        "impact_level": "high",
                        "actionable": true,
                        "recommendations": ["Continue current study approach", "Focus on maintaining consistency"],
                        "data_points": {{"improvement_rate": 0.5, "consistency_score": 0.8}}
                    }}
                ]
            }}
            """
            
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
                insights = [ProgressInsight(**insight) for insight in result.get("insights", [])]
            except json.JSONDecodeError:
                insights = self._rule_based_insights(data)
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ AI insights generation failed: {e}")
            return self._rule_based_insights(data)
    
    def _rule_based_insights(self, data: Dict[str, Any]) -> List[ProgressInsight]:
        """Generate rule-based insights when AI is not available"""
        
        insights = []
        
        # Insight 1: Score improvement
        essay_scores = data.get("essay_scores", [])
        if len(essay_scores) >= 2:
            improvement = essay_scores[-1]["overall"] - essay_scores[0]["overall"]
            if improvement > 0.5:
                insights.append(ProgressInsight(
                    insight_type="score_improvement",
                    title="Significant Score Improvement",
                    description=f"Your overall score has improved by {improvement:.1f} points",
                    confidence=0.8,
                    impact_level="high",
                    actionable=True,
                    recommendations=["Continue current study approach", "Maintain practice consistency"],
                    data_points={"improvement": improvement, "period_days": len(essay_scores) * 7}
                ))
        
        # Insight 2: Practice consistency
        practice_sessions = data.get("practice_sessions", [])
        if len(practice_sessions) > 0:
            avg_duration = statistics.mean([session["duration_minutes"] for session in practice_sessions])
            if avg_duration > 60:
                insights.append(ProgressInsight(
                    insight_type="practice_consistency",
                    title="Excellent Practice Commitment",
                    description=f"Average practice session duration: {avg_duration:.0f} minutes",
                    confidence=0.7,
                    impact_level="medium",
                    actionable=True,
                    recommendations=["Maintain current practice intensity", "Consider adding variety to practice types"],
                    data_points={"avg_duration": avg_duration, "total_sessions": len(practice_sessions)}
                ))
        
        # Insight 3: Weak area identification
        weak_areas = data.get("weak_areas", [])
        if weak_areas:
            insights.append(ProgressInsight(
                insight_type="weak_area_analysis",
                title="Focus Areas Identified",
                description=f"Areas needing attention: {', '.join(weak_areas)}",
                confidence=0.9,
                impact_level="high",
                actionable=True,
                recommendations=[f"Increase practice time for {area}" for area in weak_areas[:2]],
                data_points={"weak_areas": weak_areas}
            ))
        
        return insights[:5]  # Limit to 5 insights
    
    def _track_milestones(self, data: Dict[str, Any]) -> List[LearningMilestone]:
        """Track learning milestones"""
        
        milestones = []
        
        # Milestone 1: First essay completion
        essay_scores = data.get("essay_scores", [])
        if len(essay_scores) >= 1:
            milestones.append(LearningMilestone(
                milestone_id="first_essay",
                title="First Essay Completed",
                description="Completed your first practice essay",
                achieved_at=datetime.fromisoformat(essay_scores[0]["date"]) if essay_scores else None,
                target_date=None,
                progress_percentage=100.0,
                metrics={"essay_count": len(essay_scores)}
            ))
        
        # Milestone 2: Score improvement
        if len(essay_scores) >= 2:
            improvement = essay_scores[-1]["overall"] - essay_scores[0]["overall"]
            if improvement >= 1.0:
                milestones.append(LearningMilestone(
                    milestone_id="score_improvement",
                    title="Significant Score Improvement",
                    description=f"Improved overall score by {improvement:.1f} points",
                    achieved_at=datetime.fromisoformat(essay_scores[-1]["date"]) if essay_scores else None,
                    target_date=None,
                    progress_percentage=100.0,
                    metrics={"improvement": improvement}
                ))
        
        # Milestone 3: Target score achievement
        goals = data.get("goals", {})
        current_score = goals.get("current_band_score", 0.0)
        target_score = goals.get("target_band_score", 8.0)
        
        if current_score >= target_score:
            milestones.append(LearningMilestone(
                milestone_id="target_achieved",
                title="Target Score Achieved",
                description=f"Reached target band score of {target_score}",
                achieved_at=datetime.now(),
                target_date=datetime.fromisoformat(goals.get("target_date", "2024-03-01")) if goals.get("target_date") else None,
                progress_percentage=100.0,
                metrics={"target_score": target_score, "achieved_score": current_score}
            ))
        else:
            progress = (current_score / target_score) * 100
            milestones.append(LearningMilestone(
                milestone_id="target_progress",
                title="Working Towards Target",
                description=f"Progress towards target score of {target_score}",
                achieved_at=None,
                target_date=datetime.fromisoformat(goals.get("target_date", "2024-03-01")) if goals.get("target_date") else None,
                progress_percentage=progress,
                metrics={"target_score": target_score, "current_score": current_score}
            ))
        
        return milestones
    
    async def _generate_predictions(self, data: Dict[str, Any], learning_pattern: LearningPattern) -> Dict[str, Any]:
        """Generate predictions for future performance"""
        
        if not self.is_available:
            return self._rule_based_predictions(data, learning_pattern)
        
        try:
            # Prepare prediction data
            prediction_data = self._prepare_prediction_data(data, learning_pattern)
            
            prompt = f"""
            You are an expert learning analytics AI. Based on the following student data and learning pattern, generate predictions for future performance.

            Student Data:
            {prediction_data}

            Learning Pattern: {learning_pattern.value}

            Generate predictions for:
            1. Expected score in 30 days
            2. Time to reach target score
            3. Likelihood of achieving goals
            4. Recommended study intensity
            5. Potential challenges

            Format as JSON:
            {{
                "predicted_score_30_days": 7.5,
                "time_to_target_days": 45,
                "goal_achievement_probability": 0.85,
                "recommended_study_hours_per_week": 8,
                "potential_challenges": ["Maintaining consistency", "Grammar improvement"],
                "confidence": 0.8
            }}
            """
            
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=1500
                )
                result_text = response.choices[0].message.content
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1500,
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
                result = self._rule_based_predictions(data, learning_pattern)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ AI predictions generation failed: {e}")
            return self._rule_based_predictions(data, learning_pattern)
    
    def _rule_based_predictions(self, data: Dict[str, Any], learning_pattern: LearningPattern) -> Dict[str, Any]:
        """Generate rule-based predictions"""
        
        essay_scores = data.get("essay_scores", [])
        goals = data.get("goals", {})
        
        if not essay_scores:
            return {
                "predicted_score_30_days": 6.0,
                "time_to_target_days": 90,
                "goal_achievement_probability": 0.5,
                "recommended_study_hours_per_week": 5,
                "potential_challenges": ["Consistency", "Practice frequency"],
                "confidence": 0.6
            }
        
        current_score = essay_scores[-1]["overall"]
        target_score = goals.get("target_band_score", 8.0)
        
        # Calculate improvement rate
        if len(essay_scores) >= 2:
            improvement_rate = (essay_scores[-1]["overall"] - essay_scores[0]["overall"]) / len(essay_scores)
        else:
            improvement_rate = 0.1
        
        # Adjust based on learning pattern
        pattern_multipliers = {
            LearningPattern.ACCELERATED: 1.2,
            LearningPattern.STEADY: 1.0,
            LearningPattern.PLATEAU: 0.8,
            LearningPattern.DECLINING: 0.6,
            LearningPattern.IRREGULAR: 0.9
        }
        
        adjusted_rate = improvement_rate * pattern_multipliers.get(learning_pattern, 1.0)
        
        # Predictions
        predicted_score_30_days = min(9.0, current_score + (adjusted_rate * 4))  # 4 weeks
        time_to_target = max(30, (target_score - current_score) / max(0.1, adjusted_rate) * 7)  # Convert to days
        goal_probability = min(0.95, max(0.1, (target_score - current_score) / max(0.1, adjusted_rate) / 30))
        
        return {
            "predicted_score_30_days": round(predicted_score_30_days, 1),
            "time_to_target_days": round(time_to_target),
            "goal_achievement_probability": round(goal_probability, 2),
            "recommended_study_hours_per_week": 8 if learning_pattern == LearningPattern.ACCELERATED else 6,
            "potential_challenges": ["Consistency", "Weak area improvement"],
            "confidence": 0.7
        }
    
    def _generate_recommendations(self, insights: List[ProgressInsight], learning_pattern: LearningPattern, data: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations"""
        
        recommendations = []
        
        # Extract recommendations from insights
        for insight in insights:
            recommendations.extend(insight.recommendations)
        
        # Pattern-specific recommendations
        if learning_pattern == LearningPattern.PLATEAU:
            recommendations.extend([
                "Try different study methods to break through the plateau",
                "Focus on specific weak areas with targeted practice",
                "Consider working with a mentor or tutor"
            ])
        elif learning_pattern == LearningPattern.DECLINING:
            recommendations.extend([
                "Review and adjust your study schedule",
                "Take a short break to avoid burnout",
                "Focus on fundamentals and basic skills"
            ])
        elif learning_pattern == LearningPattern.ACCELERATED:
            recommendations.extend([
                "Maintain current momentum with consistent practice",
                "Set higher goals to continue improvement",
                "Share your success strategies with others"
            ])
        
        # Remove duplicates and limit
        unique_recommendations = list(set(recommendations))
        return unique_recommendations[:10]
    
    def _prepare_analysis_data(self, data: Dict[str, Any]) -> str:
        """Prepare data for AI analysis"""
        
        essay_scores = data.get("essay_scores", [])
        practice_sessions = data.get("practice_sessions", [])
        goals = data.get("goals", {})
        
        analysis_text = f"""
        Essay Scores: {len(essay_scores)} essays completed
        Score Range: {min([s['overall'] for s in essay_scores]) if essay_scores else 0} - {max([s['overall'] for s in essay_scores]) if essay_scores else 0}
        Current Score: {essay_scores[-1]['overall'] if essay_scores else 0}
        Target Score: {goals.get('target_band_score', 0)}
        
        Practice Sessions: {len(practice_sessions)} sessions
        Total Practice Time: {sum([s['duration_minutes'] for s in practice_sessions])} minutes
        
        Weak Areas: {', '.join(data.get('weak_areas', []))}
        Strong Areas: {', '.join(data.get('strong_areas', []))}
        """
        
        return analysis_text
    
    def _prepare_prediction_data(self, data: Dict[str, Any], learning_pattern: LearningPattern) -> str:
        """Prepare data for AI predictions"""
        
        essay_scores = data.get("essay_scores", [])
        goals = data.get("goals", {})
        
        if len(essay_scores) >= 2:
            improvement_rate = (essay_scores[-1]["overall"] - essay_scores[0]["overall"]) / len(essay_scores)
        else:
            improvement_rate = 0.1
        
        prediction_text = f"""
        Current Score: {essay_scores[-1]['overall'] if essay_scores else 0}
        Target Score: {goals.get('target_band_score', 8.0)}
        Improvement Rate: {improvement_rate:.2f} points per essay
        Learning Pattern: {learning_pattern.value}
        Practice Consistency: {len(data.get('practice_sessions', []))} sessions
        """
        
        return prediction_text
    
    def get_available_metrics(self) -> List[str]:
        """Get available progress metrics"""
        return [metric.value for metric in ProgressMetric]
    
    def get_learning_patterns(self) -> List[str]:
        """Get available learning patterns"""
        return [pattern.value for pattern in LearningPattern]
    
    def get_tracking_features(self) -> List[str]:
        """Get available tracking features"""
        return [
            "AI-powered progress analysis",
            "Learning pattern recognition",
            "Performance predictions",
            "Milestone tracking",
            "Personalized insights",
            "Goal achievement monitoring",
            "Study effectiveness analysis",
            "Weakness identification",
            "Strength recognition",
            "Recommendation generation"
        ]


