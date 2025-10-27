"""
Gamification System Service
Implements points, achievements, leaderboards, and engagement features
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import random
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class AchievementType(str, Enum):
    SCORE_BASED = "score_based"
    STREAK_BASED = "streak_based"
    PRACTICE_BASED = "practice_based"
    IMPROVEMENT_BASED = "improvement_based"
    SOCIAL_BASED = "social_based"
    MILESTONE_BASED = "milestone_based"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

class Achievement(BaseModel):
    achievement_id: str
    name: str
    description: str
    icon: str
    points: int
    difficulty: DifficultyLevel
    category: AchievementType
    requirements: Dict[str, Any]
    unlocked_at: Optional[datetime] = None
    progress: float = 0.0

class UserStats(BaseModel):
    user_id: str
    total_points: int
    level: int
    current_xp: int
    xp_to_next_level: int
    streak_days: int
    total_essays: int
    total_practice_hours: float
    achievements_unlocked: int
    rank: int
    badges: List[str]

class LeaderboardEntry(BaseModel):
    user_id: str
    username: str
    points: int
    level: int
    rank: int
    avatar: Optional[str] = None
    badge: Optional[str] = None

class Leaderboard(BaseModel):
    period: str
    entries: List[LeaderboardEntry]
    user_rank: Optional[int]
    user_points: int
    total_participants: int

class GamificationRequest(BaseModel):
    user_id: str
    action_type: str
    action_data: Dict[str, Any]
    timestamp: Optional[datetime] = None

class GamificationResponse(BaseModel):
    points_earned: int
    xp_gained: int
    level_up: bool
    new_level: Optional[int] = None
    achievements_unlocked: List[Achievement]
    streak_updated: bool
    new_streak: int
    next_milestone: Optional[Dict[str, Any]] = None

class GamificationSystem:
    """Advanced gamification system for IELTS learning"""
    
    def __init__(self):
        # Achievement definitions
        self.achievements = {
            "first_essay": Achievement(
                achievement_id="first_essay",
                name="First Steps",
                description="Complete your first essay",
                icon="🎯",
                points=50,
                difficulty=DifficultyLevel.EASY,
                category=AchievementType.PRACTICE_BASED,
                requirements={"essays_completed": 1}
            ),
            "perfect_score": Achievement(
                achievement_id="perfect_score",
                name="Perfectionist",
                description="Achieve a perfect 9.0 band score",
                icon="🏆",
                points=500,
                difficulty=DifficultyLevel.EXPERT,
                category=AchievementType.SCORE_BASED,
                requirements={"max_score": 9.0}
            ),
            "week_streak": Achievement(
                achievement_id="week_streak",
                name="Consistent Learner",
                description="Practice for 7 consecutive days",
                icon="🔥",
                points=200,
                difficulty=DifficultyLevel.MEDIUM,
                category=AchievementType.STREAK_BASED,
                requirements={"streak_days": 7}
            ),
            "month_streak": Achievement(
                achievement_id="month_streak",
                name="Dedicated Student",
                description="Practice for 30 consecutive days",
                icon="💪",
                points=1000,
                difficulty=DifficultyLevel.HARD,
                category=AchievementType.STREAK_BASED,
                requirements={"streak_days": 30}
            ),
            "improvement_master": Achievement(
                achievement_id="improvement_master",
                name="Rapid Improver",
                description="Improve by 2.0 band points in a month",
                icon="📈",
                points=300,
                difficulty=DifficultyLevel.HARD,
                category=AchievementType.IMPROVEMENT_BASED,
                requirements={"improvement_points": 2.0, "timeframe_days": 30}
            ),
            "essay_master": Achievement(
                achievement_id="essay_master",
                name="Essay Master",
                description="Complete 100 essays",
                icon="📝",
                points=400,
                difficulty=DifficultyLevel.HARD,
                category=AchievementType.PRACTICE_BASED,
                requirements={"essays_completed": 100}
            ),
            "speed_demon": Achievement(
                achievement_id="speed_demon",
                name="Speed Demon",
                description="Complete an essay in under 30 minutes",
                icon="⚡",
                points=150,
                difficulty=DifficultyLevel.MEDIUM,
                category=AchievementType.PRACTICE_BASED,
                requirements={"completion_time_minutes": 30}
            ),
            "grammar_guru": Achievement(
                achievement_id="grammar_guru",
                name="Grammar Guru",
                description="Achieve 8.0+ in grammatical range",
                icon="📚",
                points=250,
                difficulty=DifficultyLevel.HARD,
                category=AchievementType.SCORE_BASED,
                requirements={"grammar_score": 8.0}
            ),
            "vocabulary_wizard": Achievement(
                achievement_id="vocabulary_wizard",
                name="Vocabulary Wizard",
                description="Achieve 8.0+ in lexical resource",
                icon="🔮",
                points=250,
                difficulty=DifficultyLevel.HARD,
                category=AchievementType.SCORE_BASED,
                requirements={"vocabulary_score": 8.0}
            ),
            "social_butterfly": Achievement(
                achievement_id="social_butterfly",
                name="Social Butterfly",
                description="Connect with 5 mentors",
                icon="🦋",
                points=100,
                difficulty=DifficultyLevel.MEDIUM,
                category=AchievementType.SOCIAL_BASED,
                requirements={"mentor_connections": 5}
            )
        }
        
        # Points system
        self.points_system = {
            "essay_completion": 25,
            "essay_score_6": 50,
            "essay_score_7": 75,
            "essay_score_8": 100,
            "essay_score_9": 150,
            "daily_practice": 10,
            "streak_bonus": 5,
            "improvement_bonus": 20,
            "achievement_unlock": 50,
            "level_up": 100
        }
        
        # XP system (Experience Points)
        self.xp_system = {
            "essay_completion": 50,
            "essay_score_6": 100,
            "essay_score_7": 150,
            "essay_score_8": 200,
            "essay_score_9": 300,
            "daily_practice": 20,
            "streak_bonus": 10,
            "improvement_bonus": 50,
            "achievement_unlock": 100,
            "level_up": 200
        }
        
        # Level requirements (XP needed for each level)
        self.level_requirements = {
            1: 0,
            2: 500,
            3: 1200,
            4: 2100,
            5: 3200,
            6: 4500,
            7: 6000,
            8: 7700,
            9: 9600,
            10: 11700,
            11: 14000,
            12: 16500,
            13: 19200,
            14: 22100,
            15: 25200,
            16: 28500,
            17: 32000,
            18: 35700,
            19: 39600,
            20: 43700
        }
    
    async def process_action(self, request: GamificationRequest) -> GamificationResponse:
        """Process a user action and return gamification rewards"""
        
        try:
            # Get current user stats
            user_stats = self._get_user_stats(request.user_id)
            
            # Calculate points and XP
            points_earned = self._calculate_points(request.action_type, request.action_data)
            xp_gained = self._calculate_xp(request.action_type, request.action_data)
            
            # Check for level up
            level_up, new_level = self._check_level_up(user_stats, xp_gained)
            
            # Check for achievements
            achievements_unlocked = self._check_achievements(request.user_id, request.action_type, request.action_data)
            
            # Update streak
            streak_updated, new_streak = self._update_streak(request.user_id, request.action_type)
            
            # Get next milestone
            next_milestone = self._get_next_milestone(user_stats, request.action_type)
            
            # Update user stats
            self._update_user_stats(request.user_id, points_earned, xp_gained, achievements_unlocked)
            
            return GamificationResponse(
                points_earned=points_earned,
                xp_gained=xp_gained,
                level_up=level_up,
                new_level=new_level,
                achievements_unlocked=achievements_unlocked,
                streak_updated=streak_updated,
                new_streak=new_streak,
                next_milestone=next_milestone
            )
            
        except Exception as e:
            logger.error(f"❌ Gamification processing failed: {e}")
            raise e
    
    def _get_user_stats(self, user_id: str) -> UserStats:
        """Get user's current stats"""
        
        # In real implementation, this would query the database
        # For now, return sample stats
        return UserStats(
            user_id=user_id,
            total_points=1250,
            level=5,
            current_xp=3200,
            xp_to_next_level=4500,
            streak_days=12,
            total_essays=25,
            total_practice_hours=45.5,
            achievements_unlocked=8,
            rank=15,
            badges=["🔥", "📈", "🎯"]
        )
    
    def _calculate_points(self, action_type: str, action_data: Dict[str, Any]) -> int:
        """Calculate points for an action"""
        
        base_points = self.points_system.get(action_type, 0)
        
        # Add bonus points based on action data
        if action_type == "essay_completion":
            score = action_data.get("score", 0)
            if score >= 9.0:
                base_points += self.points_system["essay_score_9"]
            elif score >= 8.0:
                base_points += self.points_system["essay_score_8"]
            elif score >= 7.0:
                base_points += self.points_system["essay_score_7"]
            elif score >= 6.0:
                base_points += self.points_system["essay_score_6"]
        
        # Improvement bonus
        if action_data.get("improvement", 0) > 0.5:
            base_points += self.points_system["improvement_bonus"]
        
        return base_points
    
    def _calculate_xp(self, action_type: str, action_data: Dict[str, Any]) -> int:
        """Calculate XP for an action"""
        
        base_xp = self.xp_system.get(action_type, 0)
        
        # Add bonus XP based on action data
        if action_type == "essay_completion":
            score = action_data.get("score", 0)
            if score >= 9.0:
                base_xp += self.xp_system["essay_score_9"]
            elif score >= 8.0:
                base_xp += self.xp_system["essay_score_8"]
            elif score >= 7.0:
                base_xp += self.xp_system["essay_score_7"]
            elif score >= 6.0:
                base_xp += self.xp_system["essay_score_6"]
        
        # Improvement bonus
        if action_data.get("improvement", 0) > 0.5:
            base_xp += self.xp_system["improvement_bonus"]
        
        return base_xp
    
    def _check_level_up(self, user_stats: UserStats, xp_gained: int) -> Tuple[bool, Optional[int]]:
        """Check if user leveled up"""
        
        new_xp = user_stats.current_xp + xp_gained
        current_level = user_stats.level
        
        # Find new level
        new_level = current_level
        for level, required_xp in self.level_requirements.items():
            if new_xp >= required_xp and level > current_level:
                new_level = level
        
        level_up = new_level > current_level
        return level_up, new_level if level_up else None
    
    def _check_achievements(self, user_id: str, action_type: str, action_data: Dict[str, Any]) -> List[Achievement]:
        """Check for unlocked achievements"""
        
        unlocked_achievements = []
        
        # Get user's current progress
        user_progress = self._get_user_progress(user_id)
        
        # Check each achievement
        for achievement_id, achievement in self.achievements.items():
            if self._is_achievement_unlocked(achievement, user_progress, action_type, action_data):
                unlocked_achievements.append(achievement)
        
        return unlocked_achievements
    
    def _is_achievement_unlocked(self, achievement: Achievement, user_progress: Dict[str, Any], action_type: str, action_data: Dict[str, Any]) -> bool:
        """Check if a specific achievement is unlocked"""
        
        requirements = achievement.requirements
        
        if achievement.category == AchievementType.PRACTICE_BASED:
            if achievement.achievement_id == "first_essay":
                return action_type == "essay_completion" and user_progress.get("essays_completed", 0) == 0
            elif achievement.achievement_id == "essay_master":
                return user_progress.get("essays_completed", 0) >= requirements["essays_completed"]
            elif achievement.achievement_id == "speed_demon":
                return action_type == "essay_completion" and action_data.get("completion_time_minutes", 0) <= requirements["completion_time_minutes"]
        
        elif achievement.category == AchievementType.SCORE_BASED:
            if achievement.achievement_id == "perfect_score":
                return action_type == "essay_completion" and action_data.get("score", 0) >= requirements["max_score"]
            elif achievement.achievement_id == "grammar_guru":
                return action_type == "essay_completion" and action_data.get("grammar_score", 0) >= requirements["grammar_score"]
            elif achievement.achievement_id == "vocabulary_wizard":
                return action_type == "essay_completion" and action_data.get("vocabulary_score", 0) >= requirements["vocabulary_score"]
        
        elif achievement.category == AchievementType.STREAK_BASED:
            if achievement.achievement_id == "week_streak":
                return user_progress.get("streak_days", 0) >= requirements["streak_days"]
            elif achievement.achievement_id == "month_streak":
                return user_progress.get("streak_days", 0) >= requirements["streak_days"]
        
        elif achievement.category == AchievementType.IMPROVEMENT_BASED:
            if achievement.achievement_id == "improvement_master":
                improvement = action_data.get("improvement", 0)
                timeframe = action_data.get("timeframe_days", 0)
                return improvement >= requirements["improvement_points"] and timeframe <= requirements["timeframe_days"]
        
        elif achievement.category == AchievementType.SOCIAL_BASED:
            if achievement.achievement_id == "social_butterfly":
                return user_progress.get("mentor_connections", 0) >= requirements["mentor_connections"]
        
        return False
    
    def _update_streak(self, user_id: str, action_type: str) -> Tuple[bool, int]:
        """Update user's streak"""
        
        # In real implementation, this would check the database for last activity
        # For now, simulate streak update
        current_streak = 12  # Sample current streak
        
        if action_type in ["essay_completion", "daily_practice"]:
            new_streak = current_streak + 1
            return True, new_streak
        
        return False, current_streak
    
    def _get_next_milestone(self, user_stats: UserStats, action_type: str) -> Optional[Dict[str, Any]]:
        """Get next milestone for the user"""
        
        milestones = [
            {"type": "level", "target": user_stats.level + 1, "description": f"Reach level {user_stats.level + 1}"},
            {"type": "points", "target": (user_stats.total_points // 1000 + 1) * 1000, "description": f"Earn {(user_stats.total_points // 1000 + 1) * 1000} points"},
            {"type": "streak", "target": user_stats.streak_days + 5, "description": f"Maintain {user_stats.streak_days + 5} day streak"},
            {"type": "essays", "target": (user_stats.total_essays // 10 + 1) * 10, "description": f"Complete {(user_stats.total_essays // 10 + 1) * 10} essays"}
        ]
        
        # Return the closest milestone
        return milestones[0] if milestones else None
    
    def _get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user's progress data"""
        
        # In real implementation, this would query the database
        return {
            "essays_completed": 25,
            "streak_days": 12,
            "mentor_connections": 3,
            "total_practice_hours": 45.5,
            "best_score": 7.5,
            "improvement_rate": 1.2
        }
    
    def _update_user_stats(self, user_id: str, points_earned: int, xp_gained: int, achievements: List[Achievement]):
        """Update user's stats in the database"""
        
        # In real implementation, this would update the database
        logger.info(f"Updated stats for user {user_id}: +{points_earned} points, +{xp_gained} XP, {len(achievements)} achievements")
    
    async def get_leaderboard(self, period: str = "weekly", limit: int = 50) -> Leaderboard:
        """Get leaderboard for the specified period"""
        
        # In real implementation, this would query the database
        # For now, return sample leaderboard data
        sample_entries = [
            LeaderboardEntry(user_id="user1", username="IELTSMaster", points=2500, level=8, rank=1, badge="🏆"),
            LeaderboardEntry(user_id="user2", username="WritingPro", points=2300, level=7, rank=2, badge="🥈"),
            LeaderboardEntry(user_id="user3", username="GrammarGuru", points=2100, level=7, rank=3, badge="🥉"),
            LeaderboardEntry(user_id="user4", username="VocabularyWiz", points=1900, level=6, rank=4),
            LeaderboardEntry(user_id="user5", username="EssayExpert", points=1700, level=6, rank=5),
        ]
        
        return Leaderboard(
            period=period,
            entries=sample_entries[:limit],
            user_rank=15,
            user_points=1250,
            total_participants=150
        )
    
    async def get_user_achievements(self, user_id: str) -> Dict[str, Any]:
        """Get user's achievements"""
        
        # In real implementation, this would query the database
        unlocked_achievements = [
            self.achievements["first_essay"],
            self.achievements["week_streak"],
            self.achievements["speed_demon"]
        ]
        
        # Calculate progress for locked achievements
        user_progress = self._get_user_progress(user_id)
        locked_achievements = []
        
        for achievement_id, achievement in self.achievements.items():
            if achievement not in unlocked_achievements:
                progress = self._calculate_achievement_progress(achievement, user_progress)
                achievement.progress = progress
                locked_achievements.append(achievement)
        
        return {
            "unlocked_achievements": unlocked_achievements,
            "locked_achievements": locked_achievements,
            "total_achievements": len(self.achievements),
            "unlocked_count": len(unlocked_achievements),
            "completion_percentage": (len(unlocked_achievements) / len(self.achievements)) * 100
        }
    
    def _calculate_achievement_progress(self, achievement: Achievement, user_progress: Dict[str, Any]) -> float:
        """Calculate progress towards an achievement"""
        
        requirements = achievement.requirements
        
        if achievement.category == AchievementType.PRACTICE_BASED:
            if "essays_completed" in requirements:
                current = user_progress.get("essays_completed", 0)
                target = requirements["essays_completed"]
                return min(1.0, current / target)
        
        elif achievement.category == AchievementType.STREAK_BASED:
            if "streak_days" in requirements:
                current = user_progress.get("streak_days", 0)
                target = requirements["streak_days"]
                return min(1.0, current / target)
        
        elif achievement.category == AchievementType.SOCIAL_BASED:
            if "mentor_connections" in requirements:
                current = user_progress.get("mentor_connections", 0)
                target = requirements["mentor_connections"]
                return min(1.0, current / target)
        
        return 0.0
    
    def get_available_achievements(self) -> List[Achievement]:
        """Get all available achievements"""
        return list(self.achievements.values())
    
    def get_points_system(self) -> Dict[str, int]:
        """Get the points system configuration"""
        return self.points_system
    
    def get_xp_system(self) -> Dict[str, int]:
        """Get the XP system configuration"""
        return self.xp_system
    
    def get_level_requirements(self) -> Dict[int, int]:
        """Get level requirements"""
        return self.level_requirements


