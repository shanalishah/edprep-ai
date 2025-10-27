"""
Performance Analytics Dashboard Service
Provides comprehensive analytics and insights for user performance
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import statistics
from collections import defaultdict, Counter
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class AnalyticsPeriod(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ALL_TIME = "all_time"

class PerformanceMetric(BaseModel):
    metric_name: str
    value: float
    trend: str  # "up", "down", "stable"
    change_percentage: float
    period: str
    timestamp: datetime

class SkillAnalysis(BaseModel):
    skill_name: str
    current_level: float
    target_level: float
    improvement_rate: float
    practice_hours: float
    weak_points: List[str]
    strong_points: List[str]
    recommendations: List[str]

class PerformanceInsight(BaseModel):
    insight_type: str
    title: str
    description: str
    impact_level: str  # "high", "medium", "low"
    actionable: bool
    recommendations: List[str]
    confidence: float

class AnalyticsDashboard(BaseModel):
    user_id: str
    period: AnalyticsPeriod
    overall_performance: Dict[str, Any]
    skill_breakdown: List[SkillAnalysis]
    trends: List[PerformanceMetric]
    insights: List[PerformanceInsight]
    goals_progress: Dict[str, Any]
    comparative_analysis: Dict[str, Any]
    recommendations: List[str]

class AnalyticsRequest(BaseModel):
    user_id: str
    period: AnalyticsPeriod = AnalyticsPeriod.MONTHLY
    include_comparisons: bool = True
    include_predictions: bool = True
    focus_areas: List[str] = []

class PerformanceAnalytics:
    """Advanced performance analytics and insights generator"""
    
    def __init__(self):
        # Sample data structure for analytics
        self.sample_performance_data = {
            "essay_scores": [
                {"date": "2024-01-01", "task_achievement": 6.0, "coherence_cohesion": 5.5, "lexical_resource": 6.0, "grammatical_range": 5.5, "overall": 5.75},
                {"date": "2024-01-08", "task_achievement": 6.5, "coherence_cohesion": 6.0, "lexical_resource": 6.5, "grammatical_range": 6.0, "overall": 6.25},
                {"date": "2024-01-15", "task_achievement": 7.0, "coherence_cohesion": 6.5, "lexical_resource": 7.0, "grammatical_range": 6.5, "overall": 6.75},
                {"date": "2024-01-22", "task_achievement": 7.0, "coherence_cohesion": 7.0, "lexical_resource": 7.0, "grammatical_range": 7.0, "overall": 7.0},
            ],
            "practice_sessions": [
                {"date": "2024-01-01", "duration_minutes": 60, "type": "writing", "difficulty": "intermediate"},
                {"date": "2024-01-02", "duration_minutes": 45, "type": "reading", "difficulty": "beginner"},
                {"date": "2024-01-03", "duration_minutes": 90, "type": "writing", "difficulty": "advanced"},
                {"date": "2024-01-04", "duration_minutes": 30, "type": "listening", "difficulty": "intermediate"},
                {"date": "2024-01-05", "duration_minutes": 75, "type": "speaking", "difficulty": "intermediate"},
            ],
            "weak_areas": ["grammatical_range", "coherence_cohesion"],
            "strong_areas": ["lexical_resource", "task_achievement"],
            "target_band_score": 7.5,
            "current_band_score": 7.0
        }
    
    async def generate_dashboard(self, request: AnalyticsRequest) -> AnalyticsDashboard:
        """Generate comprehensive analytics dashboard"""
        
        try:
            # Get performance data (in real implementation, this would come from database)
            performance_data = self._get_performance_data(request.user_id, request.period)
            
            # Calculate overall performance metrics
            overall_performance = self._calculate_overall_performance(performance_data)
            
            # Analyze individual skills
            skill_breakdown = self._analyze_skills(performance_data)
            
            # Generate trends
            trends = self._generate_trends(performance_data, request.period)
            
            # Generate insights
            insights = self._generate_insights(performance_data, skill_breakdown)
            
            # Calculate goals progress
            goals_progress = self._calculate_goals_progress(performance_data)
            
            # Comparative analysis
            comparative_analysis = self._generate_comparative_analysis(performance_data) if request.include_comparisons else {}
            
            # Generate recommendations
            recommendations = self._generate_recommendations(insights, skill_breakdown)
            
            return AnalyticsDashboard(
                user_id=request.user_id,
                period=request.period,
                overall_performance=overall_performance,
                skill_breakdown=skill_breakdown,
                trends=trends,
                insights=insights,
                goals_progress=goals_progress,
                comparative_analysis=comparative_analysis,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"❌ Analytics dashboard generation failed: {e}")
            raise e
    
    def _get_performance_data(self, user_id: str, period: AnalyticsPeriod) -> Dict[str, Any]:
        """Get performance data for the specified period"""
        
        # In real implementation, this would query the database
        # For now, return sample data
        return self.sample_performance_data
    
    def _calculate_overall_performance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall performance metrics"""
        
        essay_scores = data.get("essay_scores", [])
        practice_sessions = data.get("practice_sessions", [])
        
        if not essay_scores:
            return {
                "current_score": 0.0,
                "average_score": 0.0,
                "improvement_rate": 0.0,
                "consistency": 0.0,
                "practice_hours": 0.0,
                "streak_days": 0
            }
        
        # Calculate current and average scores
        current_score = essay_scores[-1]["overall"] if essay_scores else 0.0
        average_score = statistics.mean([score["overall"] for score in essay_scores])
        
        # Calculate improvement rate
        if len(essay_scores) > 1:
            first_score = essay_scores[0]["overall"]
            last_score = essay_scores[-1]["overall"]
            improvement_rate = ((last_score - first_score) / first_score) * 100
        else:
            improvement_rate = 0.0
        
        # Calculate consistency (lower standard deviation = more consistent)
        scores = [score["overall"] for score in essay_scores]
        consistency = 1.0 - (statistics.stdev(scores) / statistics.mean(scores)) if len(scores) > 1 else 1.0
        
        # Calculate practice hours
        total_minutes = sum(session["duration_minutes"] for session in practice_sessions)
        practice_hours = total_minutes / 60.0
        
        # Calculate streak (simplified)
        streak_days = len(practice_sessions)  # In real implementation, calculate actual streak
        
        return {
            "current_score": round(current_score, 2),
            "average_score": round(average_score, 2),
            "improvement_rate": round(improvement_rate, 2),
            "consistency": round(consistency, 2),
            "practice_hours": round(practice_hours, 2),
            "streak_days": streak_days,
            "total_essays": len(essay_scores),
            "total_sessions": len(practice_sessions)
        }
    
    def _analyze_skills(self, data: Dict[str, Any]) -> List[SkillAnalysis]:
        """Analyze individual skill performance"""
        
        essay_scores = data.get("essay_scores", [])
        weak_areas = data.get("weak_areas", [])
        strong_areas = data.get("strong_areas", [])
        target_score = data.get("target_band_score", 7.0)
        
        skills = [
            "task_achievement",
            "coherence_cohesion", 
            "lexical_resource",
            "grammatical_range"
        ]
        
        skill_analyses = []
        
        for skill in skills:
            if not essay_scores:
                continue
                
            # Get current and first scores for this skill
            current_score = essay_scores[-1][skill]
            first_score = essay_scores[0][skill]
            
            # Calculate improvement rate
            improvement_rate = ((current_score - first_score) / first_score) * 100 if first_score > 0 else 0.0
            
            # Calculate practice hours for this skill
            practice_hours = self._calculate_skill_practice_hours(skill, data)
            
            # Determine weak and strong points
            weak_points = []
            strong_points = []
            
            if skill in weak_areas:
                weak_points = [f"Needs improvement in {skill.replace('_', ' ')}"]
            if skill in strong_areas:
                strong_points = [f"Strong performance in {skill.replace('_', ' ')}"]
            
            # Generate recommendations
            recommendations = self._generate_skill_recommendations(skill, current_score, target_score, weak_points)
            
            skill_analysis = SkillAnalysis(
                skill_name=skill,
                current_level=current_score,
                target_level=target_score,
                improvement_rate=improvement_rate,
                practice_hours=practice_hours,
                weak_points=weak_points,
                strong_points=strong_points,
                recommendations=recommendations
            )
            
            skill_analyses.append(skill_analysis)
        
        return skill_analyses
    
    def _generate_trends(self, data: Dict[str, Any], period: AnalyticsPeriod) -> List[PerformanceMetric]:
        """Generate performance trends"""
        
        essay_scores = data.get("essay_scores", [])
        trends = []
        
        if len(essay_scores) < 2:
            return trends
        
        # Calculate trend for overall score
        scores = [score["overall"] for score in essay_scores]
        trend_direction = "up" if scores[-1] > scores[0] else "down" if scores[-1] < scores[0] else "stable"
        change_percentage = ((scores[-1] - scores[0]) / scores[0]) * 100 if scores[0] > 0 else 0.0
        
        trends.append(PerformanceMetric(
            metric_name="Overall Score",
            value=scores[-1],
            trend=trend_direction,
            change_percentage=change_percentage,
            period=period.value,
            timestamp=datetime.now()
        ))
        
        # Calculate trend for each skill
        skills = ["task_achievement", "coherence_cohesion", "lexical_resource", "grammatical_range"]
        for skill in skills:
            skill_scores = [score[skill] for score in essay_scores]
            trend_direction = "up" if skill_scores[-1] > skill_scores[0] else "down" if skill_scores[-1] < skill_scores[0] else "stable"
            change_percentage = ((skill_scores[-1] - skill_scores[0]) / skill_scores[0]) * 100 if skill_scores[0] > 0 else 0.0
            
            trends.append(PerformanceMetric(
                metric_name=skill.replace("_", " ").title(),
                value=skill_scores[-1],
                trend=trend_direction,
                change_percentage=change_percentage,
                period=period.value,
                timestamp=datetime.now()
            ))
        
        return trends
    
    def _generate_insights(self, data: Dict[str, Any], skill_breakdown: List[SkillAnalysis]) -> List[PerformanceInsight]:
        """Generate performance insights"""
        
        insights = []
        
        # Insight 1: Overall improvement
        essay_scores = data.get("essay_scores", [])
        if len(essay_scores) >= 2:
            improvement = essay_scores[-1]["overall"] - essay_scores[0]["overall"]
            if improvement > 0.5:
                insights.append(PerformanceInsight(
                    insight_type="improvement",
                    title="Significant Improvement Detected",
                    description=f"Your overall score has improved by {improvement:.1f} points over the period.",
                    impact_level="high",
                    actionable=True,
                    recommendations=["Continue current study approach", "Focus on maintaining consistency"],
                    confidence=0.9
                ))
        
        # Insight 2: Weak area identification
        weak_areas = data.get("weak_areas", [])
        if weak_areas:
            insights.append(PerformanceInsight(
                insight_type="weakness",
                title="Weak Areas Identified",
                description=f"Focus needed on: {', '.join(weak_areas)}",
                impact_level="high",
                actionable=True,
                recommendations=[
                    f"Increase practice time for {area}" for area in weak_areas[:2]
                ],
                confidence=0.8
            ))
        
        # Insight 3: Consistency analysis
        scores = [score["overall"] for score in essay_scores]
        if len(scores) > 2:
            consistency = 1.0 - (statistics.stdev(scores) / statistics.mean(scores))
            if consistency < 0.7:
                insights.append(PerformanceInsight(
                    insight_type="consistency",
                    title="Inconsistent Performance",
                    description="Your performance varies significantly between sessions.",
                    impact_level="medium",
                    actionable=True,
                    recommendations=["Establish regular study routine", "Practice under exam conditions"],
                    confidence=0.7
                ))
        
        return insights
    
    def _calculate_goals_progress(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate progress towards goals"""
        
        current_score = data.get("current_band_score", 0.0)
        target_score = data.get("target_band_score", 7.0)
        
        progress_percentage = (current_score / target_score) * 100 if target_score > 0 else 0.0
        
        return {
            "target_score": target_score,
            "current_score": current_score,
            "progress_percentage": round(progress_percentage, 2),
            "remaining_points": round(target_score - current_score, 2),
            "estimated_time_to_goal": "4-6 weeks" if (target_score - current_score) <= 1.0 else "8-12 weeks"
        }
    
    def _generate_comparative_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comparative analysis with peers"""
        
        # Sample comparative data
        return {
            "peer_average": 6.2,
            "peer_median": 6.0,
            "user_percentile": 75,
            "above_average_skills": ["lexical_resource", "task_achievement"],
            "below_average_skills": ["grammatical_range"],
            "competitive_advantage": "Strong vocabulary and task response"
        }
    
    def _generate_recommendations(self, insights: List[PerformanceInsight], skill_breakdown: List[SkillAnalysis]) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Extract recommendations from insights
        for insight in insights:
            recommendations.extend(insight.recommendations)
        
        # Add skill-specific recommendations
        for skill in skill_breakdown:
            if skill.current_level < skill.target_level:
                recommendations.extend(skill.recommendations)
        
        # Remove duplicates and limit
        unique_recommendations = list(set(recommendations))
        return unique_recommendations[:10]
    
    def _calculate_skill_practice_hours(self, skill: str, data: Dict[str, Any]) -> float:
        """Calculate practice hours for a specific skill"""
        
        practice_sessions = data.get("practice_sessions", [])
        skill_sessions = [session for session in practice_sessions if skill in session.get("type", "")]
        
        total_minutes = sum(session["duration_minutes"] for session in skill_sessions)
        return round(total_minutes / 60.0, 2)
    
    def _generate_skill_recommendations(self, skill: str, current_score: float, target_score: float, weak_points: List[str]) -> List[str]:
        """Generate recommendations for a specific skill"""
        
        recommendations = []
        
        if current_score < target_score:
            if skill == "task_achievement":
                recommendations.extend([
                    "Practice analyzing essay prompts more carefully",
                    "Focus on addressing all parts of the question",
                    "Use the PEEL paragraph structure"
                ])
            elif skill == "coherence_cohesion":
                recommendations.extend([
                    "Practice using linking words and phrases",
                    "Work on paragraph organization",
                    "Improve logical flow between ideas"
                ])
            elif skill == "lexical_resource":
                recommendations.extend([
                    "Expand vocabulary with academic words",
                    "Practice paraphrasing",
                    "Use collocations correctly"
                ])
            elif skill == "grammatical_range":
                recommendations.extend([
                    "Practice complex sentence structures",
                    "Work on verb tenses and forms",
                    "Improve punctuation and sentence variety"
                ])
        
        return recommendations[:3]  # Limit to 3 recommendations per skill
    
    def get_available_periods(self) -> List[str]:
        """Get available analytics periods"""
        return [period.value for period in AnalyticsPeriod]
    
    def get_analytics_features(self) -> List[str]:
        """Get available analytics features"""
        return [
            "Performance tracking",
            "Skill analysis",
            "Trend identification",
            "Goal progress monitoring",
            "Comparative analysis",
            "Predictive insights",
            "Personalized recommendations",
            "Weakness identification",
            "Strength recognition",
            "Study pattern analysis"
        ]


