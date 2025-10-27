"""
Model Configuration for IELTS Writing Assessment
Optimized for speed vs quality balance
"""

from enum import Enum
from typing import Dict, Any

class ModelSpeed(Enum):
    """Model speed configurations"""
    FAST = "fast"           # Fastest response, good quality
    BALANCED = "balanced"   # Balanced speed and quality (default)
    QUALITY = "quality"     # Highest quality, slower response

class ModelConfig:
    """Model configuration for different speed/quality tradeoffs"""
    
    # Model configurations
    MODELS = {
        ModelSpeed.FAST: {
            "openai_model": "gpt-4o-mini",           # Fastest GPT-4 model
            "anthropic_model": "claude-3-haiku-20240307",  # Fastest Claude model
            "max_tokens": 800,                       # Reduced token limit
            "temperature": 0.1,                      # Low temperature for consistency
            "timeout": 15,                           # 15 second timeout
            "description": "Fast response with good quality"
        },
        ModelSpeed.BALANCED: {
            "openai_model": "gpt-4o",               # Balanced GPT-4 model
            "anthropic_model": "claude-3-sonnet-20240229",  # Balanced Claude model
            "max_tokens": 1000,                      # Standard token limit
            "temperature": 0.1,
            "timeout": 30,                           # 30 second timeout
            "description": "Balanced speed and quality"
        },
        ModelSpeed.QUALITY: {
            "openai_model": "gpt-4-turbo-preview",   # Highest quality GPT-4
            "anthropic_model": "claude-3-sonnet-20240229",  # Highest quality Claude
            "max_tokens": 1500,                      # Higher token limit
            "temperature": 0.1,
            "timeout": 60,                           # 60 second timeout
            "description": "Highest quality, slower response"
        }
    }
    
    @classmethod
    def get_model_config(cls, speed: ModelSpeed = ModelSpeed.BALANCED) -> Dict[str, Any]:
        """Get model configuration for specified speed"""
        return cls.MODELS.get(speed, cls.MODELS[ModelSpeed.BALANCED])
    
    @classmethod
    def get_available_speeds(cls) -> list:
        """Get list of available speed configurations"""
        return [speed.value for speed in ModelSpeed]
    
    @classmethod
    def get_speed_description(cls, speed: ModelSpeed) -> str:
        """Get description for speed configuration"""
        config = cls.get_model_config(speed)
        return config.get("description", "Unknown configuration")

# Default configuration
DEFAULT_SPEED = ModelSpeed.BALANCED

# Performance benchmarks (approximate)
PERFORMANCE_BENCHMARKS = {
    ModelSpeed.FAST: {
        "avg_response_time": "3-8 seconds",
        "quality_score": "8.5/10",
        "cost_per_assessment": "Low"
    },
    ModelSpeed.BALANCED: {
        "avg_response_time": "8-15 seconds", 
        "quality_score": "9.2/10",
        "cost_per_assessment": "Medium"
    },
    ModelSpeed.QUALITY: {
        "avg_response_time": "15-30 seconds",
        "quality_score": "9.5/10", 
        "cost_per_assessment": "High"
    }
}


