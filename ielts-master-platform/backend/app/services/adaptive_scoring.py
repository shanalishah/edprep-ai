"""
Adaptive Scoring System
Dynamic scoring that adapts to user performance and learning patterns
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json
import random
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ScoringMode(str, Enum):
    STANDARD = "standard"
    ADAPTIVE = "adaptive"
    CHALLENGING = "challenging"
    SUPPORTIVE = "supportive"

class PerformanceTrend(str, Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"

class AdaptiveScoringRequest(BaseModel):
    user_id: str
    essay_text: str
    prompt: str
    task_type: str
    user_history: List[Dict[str, Any]] = []
    current_level: float = 5.0
    target_level: float = 7.0
    scoring_mode: ScoringMode = ScoringMode.ADAPTIVE
    difficulty_preference: DifficultyLevel = DifficultyLevel.INTERMEDIATE

class AdaptiveScoringResponse(BaseModel):
    scores: Dict[str, float]
    overall_band_score: float
    adaptive_feedback: Dict[str, Any]
    difficulty_assessment: Dict[str, Any]
    performance_insights: Dict[str, Any]
    next_recommendations: List[str]
    scoring_methodology: str
    confidence_level: float
    processing_time: float

class PerformanceProfile(BaseModel):
    user_id: str
    current_level: float
    target_level: float
    performance_trend: PerformanceTrend
    strength_areas: List[str]
    weakness_areas: List[str]
    learning_velocity: float
    consistency_score: float
    last_updated: datetime

class DifficultyAssessment(BaseModel):
    content_difficulty: float
    vocabulary_complexity: float
    grammar_complexity: float
    coherence_level: float
    overall_difficulty: DifficultyLevel
    challenge_rating: float

class AdaptiveScoringSystem:
    """Dynamic scoring system that adapts to user performance"""
    
    def __init__(self):
        self.performance_profiles: Dict[str, PerformanceProfile] = {}
        self.scoring_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Difficulty thresholds
        self.difficulty_thresholds = {
            DifficultyLevel.BEGINNER: (1.0, 4.0),
            DifficultyLevel.INTERMEDIATE: (4.0, 6.5),
            DifficultyLevel.ADVANCED: (6.5, 8.0),
            DifficultyLevel.EXPERT: (8.0, 9.0)
        }
        
        # Scoring mode configurations
        self.scoring_modes = {
            ScoringMode.STANDARD: {
                "description": "Standard IELTS scoring criteria",
                "strictness": 1.0,
                "feedback_detail": "standard",
                "encouragement_level": "moderate"
            },
            ScoringMode.ADAPTIVE: {
                "description": "Adapts scoring based on user performance",
                "strictness": 0.8,
                "feedback_detail": "detailed",
                "encouragement_level": "high"
            },
            ScoringMode.CHALLENGING: {
                "description": "More challenging scoring to push improvement",
                "strictness": 1.2,
                "feedback_detail": "comprehensive",
                "encouragement_level": "low"
            },
            ScoringMode.SUPPORTIVE: {
                "description": "Supportive scoring to build confidence",
                "strictness": 0.7,
                "feedback_detail": "encouraging",
                "encouragement_level": "very_high"
            }
        }
        
        logger.info("AdaptiveScoringSystem initialized")
    
    async def score_essay_adaptive(self, request: AdaptiveScoringRequest) -> AdaptiveScoringResponse:
        """Score essay using adaptive methodology"""
        
        start_time = datetime.now()
        
        try:
            # Get or create user performance profile
            profile = await self._get_user_profile(request.user_id, request.user_history)
            
            # Assess essay difficulty
            difficulty_assessment = self._assess_essay_difficulty(request.essay_text, request.prompt)
            
            # Calculate adaptive scores
            adaptive_scores = await self._calculate_adaptive_scores(
                request, profile, difficulty_assessment
            )
            
            # Generate adaptive feedback
            adaptive_feedback = self._generate_adaptive_feedback(
                request, profile, adaptive_scores, difficulty_assessment
            )
            
            # Generate performance insights
            performance_insights = self._generate_performance_insights(
                profile, adaptive_scores, request.user_history
            )
            
            # Generate next recommendations
            next_recommendations = self._generate_next_recommendations(
                profile, adaptive_scores, difficulty_assessment
            )
            
            # Update user profile
            await self._update_user_profile(request.user_id, adaptive_scores, request.user_history)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AdaptiveScoringResponse(
                scores=adaptive_scores["scores"],
                overall_band_score=adaptive_scores["overall_score"],
                adaptive_feedback=adaptive_feedback,
                difficulty_assessment=difficulty_assessment.dict(),
                performance_insights=performance_insights,
                next_recommendations=next_recommendations,
                scoring_methodology=f"adaptive_{request.scoring_mode.value}",
                confidence_level=adaptive_scores["confidence"],
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"❌ Adaptive scoring failed: {e}")
            raise e
    
    async def _get_user_profile(self, user_id: str, user_history: List[Dict[str, Any]]) -> PerformanceProfile:
        """Get or create user performance profile"""
        
        if user_id in self.performance_profiles:
            profile = self.performance_profiles[user_id]
            # Update profile with recent history
            profile = self._update_profile_from_history(profile, user_history)
            return profile
        
        # Create new profile
        profile = self._create_profile_from_history(user_id, user_history)
        self.performance_profiles[user_id] = profile
        return profile
    
    def _create_profile_from_history(self, user_id: str, user_history: List[Dict[str, Any]]) -> PerformanceProfile:
        """Create performance profile from user history"""
        
        if not user_history:
            return PerformanceProfile(
                user_id=user_id,
                current_level=5.0,
                target_level=7.0,
                performance_trend=PerformanceTrend.STABLE,
                strength_areas=[],
                weakness_areas=[],
                learning_velocity=0.0,
                consistency_score=0.5,
                last_updated=datetime.now()
            )
        
        # Analyze history
        scores = [entry.get("overall_score", 5.0) for entry in user_history if "overall_score" in entry]
        current_level = scores[-1] if scores else 5.0
        
        # Calculate trend
        if len(scores) >= 3:
            recent_avg = sum(scores[-3:]) / 3
            older_avg = sum(scores[:-3]) / len(scores[:-3]) if len(scores) > 3 else recent_avg
            if recent_avg > older_avg + 0.2:
                trend = PerformanceTrend.IMPROVING
            elif recent_avg < older_avg - 0.2:
                trend = PerformanceTrend.DECLINING
            else:
                trend = PerformanceTrend.STABLE
        else:
            trend = PerformanceTrend.STABLE
        
        # Analyze strengths and weaknesses
        strength_areas, weakness_areas = self._analyze_skill_areas(user_history)
        
        # Calculate learning velocity
        learning_velocity = self._calculate_learning_velocity(scores)
        
        # Calculate consistency
        consistency_score = self._calculate_consistency(scores)
        
        return PerformanceProfile(
            user_id=user_id,
            current_level=current_level,
            target_level=7.0,  # Default target
            performance_trend=trend,
            strength_areas=strength_areas,
            weakness_areas=weakness_areas,
            learning_velocity=learning_velocity,
            consistency_score=consistency_score,
            last_updated=datetime.now()
        )
    
    def _update_profile_from_history(self, profile: PerformanceProfile, user_history: List[Dict[str, Any]]) -> PerformanceProfile:
        """Update existing profile with recent history"""
        
        if not user_history:
            return profile
        
        # Update current level
        recent_scores = [entry.get("overall_score", profile.current_level) for entry in user_history[-5:]]
        if recent_scores:
            profile.current_level = sum(recent_scores) / len(recent_scores)
        
        # Update trend
        all_scores = [entry.get("overall_score", profile.current_level) for entry in user_history]
        if len(all_scores) >= 3:
            recent_avg = sum(all_scores[-3:]) / 3
            older_avg = sum(all_scores[:-3]) / len(all_scores[:-3]) if len(all_scores) > 3 else recent_avg
            if recent_avg > older_avg + 0.2:
                profile.performance_trend = PerformanceTrend.IMPROVING
            elif recent_avg < older_avg - 0.2:
                profile.performance_trend = PerformanceTrend.DECLINING
            else:
                profile.performance_trend = PerformanceTrend.STABLE
        
        # Update strengths and weaknesses
        profile.strength_areas, profile.weakness_areas = self._analyze_skill_areas(user_history)
        
        # Update learning velocity
        profile.learning_velocity = self._calculate_learning_velocity(all_scores)
        
        # Update consistency
        profile.consistency_score = self._calculate_consistency(all_scores)
        
        profile.last_updated = datetime.now()
        return profile
    
    def _analyze_skill_areas(self, user_history: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        """Analyze user's strength and weakness areas"""
        
        skill_areas = ["task_achievement", "coherence_cohesion", "lexical_resource", "grammatical_range"]
        skill_scores = {area: [] for area in skill_areas}
        
        for entry in user_history:
            scores = entry.get("scores", {})
            for area in skill_areas:
                if area in scores:
                    skill_scores[area].append(scores[area])
        
        # Calculate average scores for each skill
        skill_averages = {}
        for area, scores in skill_scores.items():
            if scores:
                skill_averages[area] = sum(scores) / len(scores)
            else:
                skill_averages[area] = 5.0
        
        # Determine strengths and weaknesses
        overall_avg = sum(skill_averages.values()) / len(skill_averages)
        strength_areas = [area for area, score in skill_averages.items() if score > overall_avg + 0.3]
        weakness_areas = [area for area, score in skill_averages.items() if score < overall_avg - 0.3]
        
        return strength_areas, weakness_areas
    
    def _calculate_learning_velocity(self, scores: List[float]) -> float:
        """Calculate how fast the user is improving"""
        
        if len(scores) < 2:
            return 0.0
        
        # Calculate improvement rate over time
        improvements = []
        for i in range(1, len(scores)):
            improvement = scores[i] - scores[i-1]
            improvements.append(improvement)
        
        if improvements:
            return sum(improvements) / len(improvements)
        return 0.0
    
    def _calculate_consistency(self, scores: List[float]) -> float:
        """Calculate consistency of performance"""
        
        if len(scores) < 2:
            return 0.5
        
        # Calculate standard deviation
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        std_dev = variance ** 0.5
        
        # Convert to consistency score (0-1, higher is more consistent)
        consistency = max(0, 1 - (std_dev / 2))  # Assuming max std dev of 2
        return min(1, consistency)
    
    def _assess_essay_difficulty(self, essay_text: str, prompt: str) -> DifficultyAssessment:
        """Assess the difficulty level of the essay"""
        
        # Simple heuristics for difficulty assessment
        word_count = len(essay_text.split())
        sentence_count = len([s for s in essay_text.split('.') if s.strip()])
        
        # Vocabulary complexity (simple heuristic)
        complex_words = len([word for word in essay_text.split() if len(word) > 6])
        vocabulary_complexity = complex_words / word_count if word_count > 0 else 0
        
        # Grammar complexity (simple heuristic)
        complex_structures = essay_text.count(',') + essay_text.count(';') + essay_text.count(':')
        grammar_complexity = complex_structures / sentence_count if sentence_count > 0 else 0
        
        # Coherence level (simple heuristic)
        coherence_indicators = essay_text.count('however') + essay_text.count('therefore') + essay_text.count('moreover')
        coherence_level = coherence_indicators / sentence_count if sentence_count > 0 else 0
        
        # Overall difficulty
        content_difficulty = (vocabulary_complexity + grammar_complexity + coherence_level) / 3
        
        # Determine difficulty level
        if content_difficulty < 0.2:
            difficulty_level = DifficultyLevel.BEGINNER
        elif content_difficulty < 0.4:
            difficulty_level = DifficultyLevel.INTERMEDIATE
        elif content_difficulty < 0.6:
            difficulty_level = DifficultyLevel.ADVANCED
        else:
            difficulty_level = DifficultyLevel.EXPERT
        
        # Challenge rating (0-1)
        challenge_rating = min(1.0, content_difficulty * 2)
        
        return DifficultyAssessment(
            content_difficulty=content_difficulty,
            vocabulary_complexity=vocabulary_complexity,
            grammar_complexity=grammar_complexity,
            coherence_level=coherence_level,
            overall_difficulty=difficulty_level,
            challenge_rating=challenge_rating
        )
    
    async def _calculate_adaptive_scores(self, request: AdaptiveScoringRequest, profile: PerformanceProfile, difficulty: DifficultyAssessment) -> Dict[str, Any]:
        """Calculate adaptive scores based on user profile and difficulty"""
        
        # Base scores (simplified calculation)
        base_scores = {
            "task_achievement": 6.0,
            "coherence_cohesion": 6.0,
            "lexical_resource": 6.0,
            "grammatical_range": 6.0
        }
        
        # Apply difficulty adjustments
        difficulty_factor = difficulty.challenge_rating
        
        # Apply user profile adjustments
        profile_factor = self._calculate_profile_factor(profile)
        
        # Apply scoring mode adjustments
        mode_config = self.scoring_modes[request.scoring_mode]
        strictness_factor = mode_config["strictness"]
        
        # Calculate final scores
        adaptive_scores = {}
        for skill, base_score in base_scores.items():
            # Adjust based on user's performance in this skill
            if skill in profile.strength_areas:
                skill_adjustment = 0.5
            elif skill in profile.weakness_areas:
                skill_adjustment = -0.5
            else:
                skill_adjustment = 0.0
            
            # Apply all adjustments
            adjusted_score = base_score + skill_adjustment + (difficulty_factor - 0.5) + (profile_factor - 0.5)
            
            # Apply strictness
            if request.scoring_mode == ScoringMode.CHALLENGING:
                adjusted_score *= 0.9  # Make it harder
            elif request.scoring_mode == ScoringMode.SUPPORTIVE:
                adjusted_score *= 1.1  # Make it easier
            
            # Clamp to valid range and round to 0.5
            adjusted_score = max(1.0, min(9.0, adjusted_score))
            adaptive_scores[skill] = round(adjusted_score * 2) / 2
        
        # Calculate overall score
        overall_score = sum(adaptive_scores.values()) / len(adaptive_scores)
        overall_score = round(overall_score * 2) / 2
        
        # Calculate confidence
        confidence = self._calculate_confidence(profile, difficulty, request.scoring_mode)
        
        return {
            "scores": adaptive_scores,
            "overall_score": overall_score,
            "confidence": confidence
        }
    
    def _calculate_profile_factor(self, profile: PerformanceProfile) -> float:
        """Calculate adjustment factor based on user profile"""
        
        # Base factor from current level
        level_factor = (profile.current_level - 5.0) / 4.0  # Normalize to 0-1
        
        # Adjust for trend
        if profile.performance_trend == PerformanceTrend.IMPROVING:
            trend_factor = 0.1
        elif profile.performance_trend == PerformanceTrend.DECLINING:
            trend_factor = -0.1
        else:
            trend_factor = 0.0
        
        # Adjust for consistency
        consistency_factor = (profile.consistency_score - 0.5) * 0.2
        
        # Adjust for learning velocity
        velocity_factor = min(0.2, max(-0.2, profile.learning_velocity * 0.1))
        
        return level_factor + trend_factor + consistency_factor + velocity_factor
    
    def _calculate_confidence(self, profile: PerformanceProfile, difficulty: DifficultyAssessment, scoring_mode: ScoringMode) -> float:
        """Calculate confidence level for the scoring"""
        
        base_confidence = 0.8
        
        # Adjust for profile completeness
        if profile.consistency_score > 0.7:
            base_confidence += 0.1
        
        # Adjust for difficulty match
        if difficulty.overall_difficulty.value in [level.value for level in self.difficulty_thresholds.keys()]:
            base_confidence += 0.05
        
        # Adjust for scoring mode
        if scoring_mode == ScoringMode.ADAPTIVE:
            base_confidence += 0.05
        
        return min(1.0, base_confidence)
    
    def _generate_adaptive_feedback(self, request: AdaptiveScoringRequest, profile: PerformanceProfile, scores: Dict[str, Any], difficulty: DifficultyAssessment) -> Dict[str, Any]:
        """Generate adaptive feedback based on user profile and performance"""
        
        mode_config = self.scoring_modes[request.scoring_mode]
        
        feedback = {
            "overall_message": self._generate_overall_message(profile, scores, mode_config),
            "strength_areas": self._generate_strength_feedback(profile.strength_areas, scores),
            "improvement_areas": self._generate_improvement_feedback(profile.weakness_areas, scores),
            "adaptive_suggestions": self._generate_adaptive_suggestions(profile, difficulty),
            "encouragement_level": mode_config["encouragement_level"],
            "feedback_detail": mode_config["feedback_detail"]
        }
        
        return feedback
    
    def _generate_overall_message(self, profile: PerformanceProfile, scores: Dict[str, Any], mode_config: Dict[str, Any]) -> str:
        """Generate overall feedback message"""
        
        overall_score = scores["overall_score"]
        
        if mode_config["encouragement_level"] == "very_high":
            return f"Great work! You're making excellent progress. Your current score of {overall_score} shows you're on the right track to reaching your {profile.target_level} target."
        elif mode_config["encouragement_level"] == "high":
            return f"Good effort! Your score of {overall_score} demonstrates solid understanding. Keep practicing to reach your {profile.target_level} goal."
        elif mode_config["encouragement_level"] == "moderate":
            return f"Your score of {overall_score} shows room for improvement. Focus on the areas we've identified to reach your {profile.target_level} target."
        else:  # low
            return f"Your score of {overall_score} indicates significant areas for improvement. Dedicated practice in weak areas will help you reach your {profile.target_level} goal."
    
    def _generate_strength_feedback(self, strength_areas: List[str], scores: Dict[str, Any]) -> List[str]:
        """Generate feedback for strength areas"""
        
        feedback = []
        for area in strength_areas:
            if area in scores:
                score = scores[area]
                feedback.append(f"Excellent work in {area.replace('_', ' ')} (Score: {score}). This is one of your strongest areas.")
        
        return feedback
    
    def _generate_improvement_feedback(self, weakness_areas: List[str], scores: Dict[str, Any]) -> List[str]:
        """Generate feedback for improvement areas"""
        
        feedback = []
        for area in weakness_areas:
            if area in scores:
                score = scores[area]
                feedback.append(f"Focus on improving {area.replace('_', ' ')} (Score: {score}). This area needs more attention.")
        
        return feedback
    
    def _generate_adaptive_suggestions(self, profile: PerformanceProfile, difficulty: DifficultyAssessment) -> List[str]:
        """Generate adaptive suggestions based on profile and difficulty"""
        
        suggestions = []
        
        # Suggestions based on performance trend
        if profile.performance_trend == PerformanceTrend.IMPROVING:
            suggestions.append("Keep up the excellent progress! Your improvement trend is positive.")
        elif profile.performance_trend == PerformanceTrend.DECLINING:
            suggestions.append("Consider reviewing your study approach. Your recent performance shows a decline.")
        
        # Suggestions based on consistency
        if profile.consistency_score < 0.5:
            suggestions.append("Work on maintaining consistent performance. Regular practice will help stabilize your scores.")
        
        # Suggestions based on difficulty
        if difficulty.challenge_rating > 0.7:
            suggestions.append("This was a challenging essay. Great job tackling difficult content!")
        elif difficulty.challenge_rating < 0.3:
            suggestions.append("Try more challenging prompts to push your skills further.")
        
        # Suggestions based on learning velocity
        if profile.learning_velocity > 0.1:
            suggestions.append("Your learning velocity is excellent! You're improving quickly.")
        elif profile.learning_velocity < -0.1:
            suggestions.append("Consider adjusting your study methods. Your progress has slowed recently.")
        
        return suggestions
    
    def _generate_performance_insights(self, profile: PerformanceProfile, scores: Dict[str, Any], user_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate performance insights"""
        
        insights = {
            "performance_trend": profile.performance_trend.value,
            "learning_velocity": profile.learning_velocity,
            "consistency_score": profile.consistency_score,
            "strength_areas": profile.strength_areas,
            "weakness_areas": profile.weakness_areas,
            "improvement_potential": self._calculate_improvement_potential(profile),
            "study_efficiency": self._calculate_study_efficiency(profile, user_history),
            "goal_progress": self._calculate_goal_progress(profile, scores["overall_score"])
        }
        
        return insights
    
    def _calculate_improvement_potential(self, profile: PerformanceProfile) -> float:
        """Calculate potential for improvement"""
        
        # Based on current level vs target
        level_gap = profile.target_level - profile.current_level
        
        # Based on learning velocity
        velocity_factor = max(0, profile.learning_velocity)
        
        # Based on consistency
        consistency_factor = profile.consistency_score
        
        # Calculate potential (0-1)
        potential = min(1.0, (level_gap / 4.0) + (velocity_factor * 0.3) + (consistency_factor * 0.2))
        return potential
    
    def _calculate_study_efficiency(self, profile: PerformanceProfile, user_history: List[Dict[str, Any]]) -> float:
        """Calculate study efficiency"""
        
        if not user_history:
            return 0.5
        
        # Simple efficiency calculation based on improvement per submission
        scores = [entry.get("overall_score", profile.current_level) for entry in user_history]
        if len(scores) < 2:
            return 0.5
        
        improvement = scores[-1] - scores[0]
        efficiency = improvement / len(scores)
        
        return min(1.0, max(0.0, efficiency))
    
    def _calculate_goal_progress(self, profile: PerformanceProfile, current_score: float) -> Dict[str, Any]:
        """Calculate progress toward goal"""
        
        total_gap = profile.target_level - profile.current_level
        current_gap = profile.target_level - current_score
        
        if total_gap <= 0:
            progress_percentage = 100.0
        else:
            progress_percentage = ((total_gap - current_gap) / total_gap) * 100
        
        return {
            "progress_percentage": round(progress_percentage, 1),
            "remaining_gap": round(current_gap, 1),
            "estimated_time_to_goal": self._estimate_time_to_goal(profile, current_gap)
        }
    
    def _estimate_time_to_goal(self, profile: PerformanceProfile, remaining_gap: float) -> str:
        """Estimate time to reach goal"""
        
        if remaining_gap <= 0:
            return "Goal achieved!"
        
        # Based on learning velocity
        if profile.learning_velocity > 0.1:
            weeks = remaining_gap / (profile.learning_velocity * 4)  # Assuming weekly practice
        elif profile.learning_velocity > 0:
            weeks = remaining_gap / (profile.learning_velocity * 2)
        else:
            weeks = remaining_gap * 4  # Conservative estimate
        
        if weeks < 4:
            return f"{int(weeks)} weeks"
        elif weeks < 12:
            return f"{int(weeks/4)} months"
        else:
            return f"{int(weeks/12)} months"
    
    def _generate_next_recommendations(self, profile: PerformanceProfile, scores: Dict[str, Any], difficulty: DifficultyAssessment) -> List[str]:
        """Generate next step recommendations"""
        
        recommendations = []
        
        # Recommendations based on weakness areas
        for area in profile.weakness_areas:
            recommendations.append(f"Focus on {area.replace('_', ' ')} practice exercises")
        
        # Recommendations based on difficulty
        if difficulty.challenge_rating > 0.7:
            recommendations.append("Try more challenging prompts to push your skills")
        elif difficulty.challenge_rating < 0.3:
            recommendations.append("Practice with more complex vocabulary and sentence structures")
        
        # Recommendations based on consistency
        if profile.consistency_score < 0.6:
            recommendations.append("Establish a regular practice schedule for better consistency")
        
        # Recommendations based on learning velocity
        if profile.learning_velocity < 0.05:
            recommendations.append("Consider adjusting your study methods for faster improvement")
        
        # General recommendations
        recommendations.extend([
            "Review your mistakes and learn from them",
            "Practice regularly to maintain improvement",
            "Set specific weekly goals for each skill area"
        ])
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    async def _update_user_profile(self, user_id: str, scores: Dict[str, Any], user_history: List[Dict[str, Any]]):
        """Update user profile with new scoring data"""
        
        if user_id in self.performance_profiles:
            profile = self.performance_profiles[user_id]
            profile = self._update_profile_from_history(profile, user_history)
            self.performance_profiles[user_id] = profile
    
    def get_scoring_modes(self) -> List[str]:
        """Get available scoring modes"""
        return [mode.value for mode in ScoringMode]
    
    def get_difficulty_levels(self) -> List[str]:
        """Get available difficulty levels"""
        return [level.value for level in DifficultyLevel]
    
    def get_adaptive_features(self) -> List[str]:
        """Get available adaptive features"""
        return [
            "Dynamic difficulty assessment",
            "Performance-based scoring adjustments",
            "Personalized feedback generation",
            "Learning velocity tracking",
            "Consistency analysis",
            "Strength and weakness identification",
            "Goal progress tracking",
            "Study efficiency measurement",
            "Adaptive recommendations",
            "Multiple scoring modes"
        ]


