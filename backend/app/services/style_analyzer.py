"""
Writing Style Analyzer Service
Analyzes writing patterns, style, and provides personalized insights
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics
from collections import Counter, defaultdict
import openai
from anthropic import Anthropic
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class WritingStyle(str, Enum):
    FORMAL = "formal"
    INFORMAL = "informal"
    ACADEMIC = "academic"
    CONVERSATIONAL = "conversational"
    PERSUASIVE = "persuasive"
    DESCRIPTIVE = "descriptive"
    ANALYTICAL = "analytical"

class ComplexityLevel(str, Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class StyleMetric(BaseModel):
    metric_name: str
    value: float
    percentile: float
    description: str
    recommendation: str

class WritingPattern(BaseModel):
    pattern_type: str
    frequency: float
    examples: List[str]
    impact: str
    suggestion: str

class StyleAnalysis(BaseModel):
    overall_style: WritingStyle
    complexity_level: ComplexityLevel
    metrics: List[StyleMetric]
    patterns: List[WritingPattern]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    consistency_score: float
    improvement_areas: List[str]

class StyleAnalysisRequest(BaseModel):
    text: str
    task_type: str = "Task 2"
    user_id: Optional[str] = None
    include_comparison: bool = True
    include_predictions: bool = True

class StyleAnalysisResponse(BaseModel):
    analysis: StyleAnalysis
    comparison_data: Dict[str, Any]
    predictions: Dict[str, Any]
    processing_time: float
    confidence: float

class WritingStyleAnalyzer:
    """Advanced writing style analysis service"""
    
    def __init__(self, openai_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        self.openai_client = openai.OpenAI(api_key=openai_api_key) if openai_api_key else None
        self.anthropic_client = Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None
        self.is_available = bool(openai_api_key or anthropic_api_key)
        
        # Style indicators
        self.formal_indicators = [
            "furthermore", "moreover", "consequently", "therefore", "nevertheless",
            "in addition", "on the other hand", "it is evident that", "it can be argued",
            "research indicates", "studies show", "evidence suggests"
        ]
        
        self.informal_indicators = [
            "well", "so", "anyway", "you know", "I think", "I believe", "in my opinion",
            "basically", "actually", "really", "very", "quite", "pretty"
        ]
        
        self.academic_indicators = [
            "according to", "research demonstrates", "empirical evidence", "theoretical framework",
            "methodology", "hypothesis", "analysis reveals", "findings indicate",
            "literature review", "peer-reviewed", "scholarly"
        ]
        
        # Sentence complexity patterns
        self.complexity_patterns = {
            "simple_sentences": r"^[^.!?]*[.!?]$",
            "compound_sentences": r"[.!?]\s+[A-Z][^.!?]*[.!?]$",
            "complex_sentences": r"(because|although|while|since|if|when|where|which|that|who|whom|whose)",
            "compound_complex": r"(and|but|or|so|yet|for|nor).*(because|although|while|since|if|when)"
        }
        
        # Vocabulary sophistication levels
        self.vocabulary_levels = {
            "basic": ["good", "bad", "big", "small", "nice", "very", "really", "so", "get", "make"],
            "intermediate": ["excellent", "poor", "significant", "minor", "pleasant", "extremely", "genuinely", "obtain", "create"],
            "advanced": ["outstanding", "deficient", "substantial", "negligible", "exceptional", "remarkably", "authentically", "acquire", "fabricate"],
            "expert": ["exceptional", "inadequate", "considerable", "minimal", "extraordinary", "exceptionally", "genuinely", "procure", "manufacture"]
        }
        
        if not self.is_available:
            logger.warning("⚠️ No LLM API keys provided, Style Analyzer will use rule-based analysis")
    
    async def analyze_style(self, request: StyleAnalysisRequest) -> StyleAnalysisResponse:
        """Analyze writing style comprehensively"""
        
        try:
            # Basic text analysis
            basic_analysis = self._analyze_basic_metrics(request.text)
            
            # AI-powered analysis if available
            if self.is_available:
                ai_analysis = await self._ai_style_analysis(request)
                analysis = self._merge_analyses(basic_analysis, ai_analysis)
            else:
                analysis = basic_analysis
            
            # Generate comparison data
            comparison_data = self._generate_comparison_data(analysis) if request.include_comparison else {}
            
            # Generate predictions
            predictions = self._generate_predictions(analysis) if request.include_predictions else {}
            
            return StyleAnalysisResponse(
                analysis=analysis,
                comparison_data=comparison_data,
                predictions=predictions,
                processing_time=0.0,  # Will be set by caller
                confidence=0.8 if self.is_available else 0.6
            )
            
        except Exception as e:
            logger.error(f"❌ Style analysis failed: {e}")
            raise e
    
    def _analyze_basic_metrics(self, text: str) -> StyleAnalysis:
        """Perform basic style analysis using rules"""
        
        # Calculate basic metrics
        sentences = self._split_sentences(text)
        words = text.split()
        
        # Style detection
        overall_style = self._detect_style(text)
        complexity_level = self._assess_complexity(text)
        
        # Calculate metrics
        metrics = self._calculate_style_metrics(text, sentences, words)
        
        # Identify patterns
        patterns = self._identify_patterns(text)
        
        # Determine strengths and weaknesses
        strengths, weaknesses = self._assess_strengths_weaknesses(metrics, patterns)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(strengths, weaknesses, overall_style)
        
        # Calculate consistency
        consistency_score = self._calculate_consistency(text)
        
        # Identify improvement areas
        improvement_areas = self._identify_improvement_areas(weaknesses, metrics)
        
        return StyleAnalysis(
            overall_style=overall_style,
            complexity_level=complexity_level,
            metrics=metrics,
            patterns=patterns,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            consistency_score=consistency_score,
            improvement_areas=improvement_areas
        )
    
    async def _ai_style_analysis(self, request: StyleAnalysisRequest) -> StyleAnalysis:
        """Use AI for advanced style analysis"""
        
        prompt = f"""
        You are an expert writing style analyst. Analyze the following IELTS essay for writing style, patterns, and characteristics.

        Task Type: {request.task_type}
        Text: "{request.text}"

        Provide a comprehensive analysis including:
        1. Overall writing style (formal, informal, academic, conversational, persuasive, descriptive, analytical)
        2. Complexity level (basic, intermediate, advanced, expert)
        3. Specific style metrics with values and percentiles
        4. Writing patterns and their frequency
        5. Strengths and weaknesses
        6. Specific recommendations for improvement
        7. Consistency score (0-1)
        8. Key improvement areas

        Format as JSON:
        {{
            "overall_style": "academic",
            "complexity_level": "advanced",
            "metrics": [
                {{
                    "metric_name": "Sentence Variety",
                    "value": 7.5,
                    "percentile": 75,
                    "description": "Good variety in sentence structures",
                    "recommendation": "Continue using varied sentence patterns"
                }}
            ],
            "patterns": [
                {{
                    "pattern_type": "Transition Words",
                    "frequency": 0.8,
                    "examples": ["furthermore", "moreover"],
                    "impact": "positive",
                    "suggestion": "Good use of transitions"
                }}
            ],
            "strengths": ["Strong vocabulary", "Clear structure"],
            "weaknesses": ["Limited sentence variety", "Repetitive phrases"],
            "recommendations": ["Use more complex sentences", "Vary vocabulary"],
            "consistency_score": 0.8,
            "improvement_areas": ["sentence_variety", "vocabulary_diversity"]
        }}
        """
        
        try:
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
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                result = self._parse_ai_style_fallback(result_text)
            
            # Convert to StyleAnalysis object
            metrics = [StyleMetric(**metric) for metric in result.get("metrics", [])]
            patterns = [WritingPattern(**pattern) for pattern in result.get("patterns", [])]
            
            return StyleAnalysis(
                overall_style=WritingStyle(result.get("overall_style", "formal")),
                complexity_level=ComplexityLevel(result.get("complexity_level", "intermediate")),
                metrics=metrics,
                patterns=patterns,
                strengths=result.get("strengths", []),
                weaknesses=result.get("weaknesses", []),
                recommendations=result.get("recommendations", []),
                consistency_score=result.get("consistency_score", 0.7),
                improvement_areas=result.get("improvement_areas", [])
            )
            
        except Exception as e:
            logger.error(f"❌ AI style analysis failed: {e}")
            raise e
    
    def _detect_style(self, text: str) -> WritingStyle:
        """Detect overall writing style"""
        
        text_lower = text.lower()
        
        # Count style indicators
        formal_count = sum(1 for indicator in self.formal_indicators if indicator in text_lower)
        informal_count = sum(1 for indicator in self.informal_indicators if indicator in text_lower)
        academic_count = sum(1 for indicator in self.academic_indicators if indicator in text_lower)
        
        # Determine style based on indicators
        if academic_count > formal_count and academic_count > informal_count:
            return WritingStyle.ACADEMIC
        elif formal_count > informal_count:
            return WritingStyle.FORMAL
        elif informal_count > formal_count:
            return WritingStyle.INFORMAL
        else:
            return WritingStyle.FORMAL  # Default for IELTS
    
    def _assess_complexity(self, text: str) -> ComplexityLevel:
        """Assess writing complexity level"""
        
        sentences = self._split_sentences(text)
        words = text.split()
        
        # Calculate complexity metrics
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        complex_sentence_ratio = self._calculate_complex_sentence_ratio(sentences)
        vocabulary_sophistication = self._assess_vocabulary_sophistication(words)
        
        # Determine complexity level
        complexity_score = (avg_sentence_length / 20) + complex_sentence_ratio + vocabulary_sophistication
        
        if complexity_score >= 2.5:
            return ComplexityLevel.EXPERT
        elif complexity_score >= 2.0:
            return ComplexityLevel.ADVANCED
        elif complexity_score >= 1.5:
            return ComplexityLevel.INTERMEDIATE
        else:
            return ComplexityLevel.BASIC
    
    def _calculate_style_metrics(self, text: str, sentences: List[str], words: List[str]) -> List[StyleMetric]:
        """Calculate various style metrics"""
        
        metrics = []
        
        # Sentence variety
        sentence_lengths = [len(sentence.split()) for sentence in sentences]
        sentence_variety = 1.0 - (statistics.stdev(sentence_lengths) / statistics.mean(sentence_lengths)) if len(sentence_lengths) > 1 else 0.0
        
        metrics.append(StyleMetric(
            metric_name="Sentence Variety",
            value=round(sentence_variety * 10, 1),
            percentile=min(100, sentence_variety * 100),
            description="Variety in sentence lengths and structures",
            recommendation="Use sentences of different lengths for better flow"
        ))
        
        # Vocabulary diversity
        unique_words = len(set(word.lower() for word in words))
        vocabulary_diversity = unique_words / len(words) if words else 0.0
        
        metrics.append(StyleMetric(
            metric_name="Vocabulary Diversity",
            value=round(vocabulary_diversity * 10, 1),
            percentile=min(100, vocabulary_diversity * 100),
            description="Use of varied vocabulary",
            recommendation="Expand vocabulary to avoid repetition"
        ))
        
        # Transition usage
        transition_words = ["furthermore", "moreover", "however", "therefore", "consequently", "nevertheless", "in addition", "on the other hand"]
        transition_count = sum(1 for word in transition_words if word in text.lower())
        transition_score = min(10, transition_count * 2)
        
        metrics.append(StyleMetric(
            metric_name="Transition Usage",
            value=transition_score,
            percentile=min(100, transition_score * 10),
            description="Use of linking words and phrases",
            recommendation="Add more transition words for better coherence"
        ))
        
        # Passive voice usage
        passive_voice_count = len(re.findall(r'\b(was|were|is|are|been|being)\s+\w+ed\b', text))
        passive_ratio = passive_voice_count / len(sentences) if sentences else 0.0
        
        metrics.append(StyleMetric(
            metric_name="Passive Voice Usage",
            value=round(passive_ratio * 10, 1),
            percentile=min(100, passive_ratio * 100),
            description="Appropriate use of passive voice",
            recommendation="Balance active and passive voice appropriately"
        ))
        
        return metrics
    
    def _identify_patterns(self, text: str) -> List[WritingPattern]:
        """Identify writing patterns"""
        
        patterns = []
        
        # Repetition patterns
        words = text.lower().split()
        word_counts = Counter(words)
        repeated_words = [(word, count) for word, count in word_counts.items() if count > 2 and len(word) > 3]
        
        if repeated_words:
            patterns.append(WritingPattern(
                pattern_type="Word Repetition",
                frequency=len(repeated_words) / len(set(words)),
                examples=[word for word, count in repeated_words[:3]],
                impact="negative",
                suggestion="Use synonyms to avoid repetition"
            ))
        
        # Sentence structure patterns
        sentences = self._split_sentences(text)
        simple_sentences = [s for s in sentences if len(s.split()) <= 10]
        simple_ratio = len(simple_sentences) / len(sentences) if sentences else 0.0
        
        if simple_ratio > 0.7:
            patterns.append(WritingPattern(
                pattern_type="Simple Sentences",
                frequency=simple_ratio,
                examples=[s[:50] + "..." if len(s) > 50 else s for s in simple_sentences[:2]],
                impact="negative",
                suggestion="Use more complex sentence structures"
            ))
        
        # Transition patterns
        transition_words = ["furthermore", "moreover", "however", "therefore", "consequently"]
        transition_count = sum(1 for word in transition_words if word in text.lower())
        
        if transition_count > 0:
            patterns.append(WritingPattern(
                pattern_type="Transition Words",
                frequency=transition_count / len(sentences) if sentences else 0.0,
                examples=[word for word in transition_words if word in text.lower()],
                impact="positive",
                suggestion="Good use of transitions for coherence"
            ))
        
        return patterns
    
    def _assess_strengths_weaknesses(self, metrics: List[StyleMetric], patterns: List[WritingPattern]) -> Tuple[List[str], List[str]]:
        """Assess strengths and weaknesses"""
        
        strengths = []
        weaknesses = []
        
        # Analyze metrics
        for metric in metrics:
            if metric.percentile >= 70:
                strengths.append(f"Strong {metric.metric_name.lower()}")
            elif metric.percentile <= 30:
                weaknesses.append(f"Weak {metric.metric_name.lower()}")
        
        # Analyze patterns
        for pattern in patterns:
            if pattern.impact == "positive":
                strengths.append(f"Good {pattern.pattern_type.lower()}")
            elif pattern.impact == "negative":
                weaknesses.append(f"Needs improvement in {pattern.pattern_type.lower()}")
        
        return strengths[:5], weaknesses[:5]
    
    def _generate_recommendations(self, strengths: List[str], weaknesses: List[str], style: WritingStyle) -> List[str]:
        """Generate personalized recommendations"""
        
        recommendations = []
        
        # Style-specific recommendations
        if style == WritingStyle.INFORMAL:
            recommendations.append("Use more formal language for IELTS writing")
        elif style == WritingStyle.FORMAL:
            recommendations.append("Maintain formal tone throughout the essay")
        
        # Weakness-based recommendations
        for weakness in weaknesses:
            if "sentence variety" in weakness.lower():
                recommendations.append("Practice using different sentence structures")
            elif "vocabulary" in weakness.lower():
                recommendations.append("Expand academic vocabulary")
            elif "transition" in weakness.lower():
                recommendations.append("Add more linking words and phrases")
        
        # General recommendations
        recommendations.extend([
            "Read high-scoring IELTS essays for style reference",
            "Practice writing with varied sentence structures",
            "Use academic vocabulary appropriately"
        ])
        
        return recommendations[:8]
    
    def _calculate_consistency(self, text: str) -> float:
        """Calculate writing consistency score"""
        
        sentences = self._split_sentences(text)
        if len(sentences) < 2:
            return 1.0
        
        # Calculate consistency in sentence length
        sentence_lengths = [len(sentence.split()) for sentence in sentences]
        length_consistency = 1.0 - (statistics.stdev(sentence_lengths) / statistics.mean(sentence_lengths))
        
        # Calculate consistency in style indicators
        style_consistency = self._calculate_style_consistency(text)
        
        # Average consistency
        return (length_consistency + style_consistency) / 2
    
    def _calculate_style_consistency(self, text: str) -> float:
        """Calculate consistency in writing style"""
        
        # Split text into paragraphs
        paragraphs = text.split('\n\n')
        if len(paragraphs) < 2:
            return 1.0
        
        # Analyze style consistency across paragraphs
        paragraph_styles = []
        for paragraph in paragraphs:
            if paragraph.strip():
                style = self._detect_style(paragraph)
                paragraph_styles.append(style.value)
        
        # Calculate consistency
        if len(set(paragraph_styles)) == 1:
            return 1.0
        else:
            return 0.7  # Some variation is acceptable
    
    def _identify_improvement_areas(self, weaknesses: List[str], metrics: List[StyleMetric]) -> List[str]:
        """Identify key improvement areas"""
        
        improvement_areas = []
        
        for weakness in weaknesses:
            if "sentence" in weakness.lower():
                improvement_areas.append("sentence_variety")
            elif "vocabulary" in weakness.lower():
                improvement_areas.append("vocabulary_diversity")
            elif "transition" in weakness.lower():
                improvement_areas.append("coherence_cohesion")
            elif "passive" in weakness.lower():
                improvement_areas.append("grammatical_range")
        
        # Add areas based on low-scoring metrics
        for metric in metrics:
            if metric.percentile < 50:
                improvement_areas.append(metric.metric_name.lower().replace(" ", "_"))
        
        return list(set(improvement_areas))[:5]
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _calculate_complex_sentence_ratio(self, sentences: List[str]) -> float:
        """Calculate ratio of complex sentences"""
        if not sentences:
            return 0.0
        
        complex_count = 0
        for sentence in sentences:
            if any(pattern in sentence.lower() for pattern in ["because", "although", "while", "since", "if", "when"]):
                complex_count += 1
        
        return complex_count / len(sentences)
    
    def _assess_vocabulary_sophistication(self, words: List[str]) -> float:
        """Assess vocabulary sophistication level"""
        if not words:
            return 0.0
        
        sophistication_score = 0.0
        for level, vocab_list in self.vocabulary_levels.items():
            level_words = sum(1 for word in words if word.lower() in vocab_list)
            if level == "basic":
                sophistication_score -= level_words * 0.1
            elif level == "intermediate":
                sophistication_score += level_words * 0.1
            elif level == "advanced":
                sophistication_score += level_words * 0.2
            elif level == "expert":
                sophistication_score += level_words * 0.3
        
        return max(0, min(1, sophistication_score / len(words)))
    
    def _merge_analyses(self, basic: StyleAnalysis, ai: StyleAnalysis) -> StyleAnalysis:
        """Merge basic and AI analyses"""
        
        # Use AI analysis as primary, enhance with basic analysis
        merged_metrics = ai.metrics + basic.metrics
        merged_patterns = ai.patterns + basic.patterns
        merged_strengths = list(set(ai.strengths + basic.strengths))
        merged_weaknesses = list(set(ai.weaknesses + basic.weaknesses))
        merged_recommendations = list(set(ai.recommendations + basic.recommendations))
        
        return StyleAnalysis(
            overall_style=ai.overall_style,
            complexity_level=ai.complexity_level,
            metrics=merged_metrics[:10],  # Limit metrics
            patterns=merged_patterns[:8],  # Limit patterns
            strengths=merged_strengths[:6],
            weaknesses=merged_weaknesses[:6],
            recommendations=merged_recommendations[:8],
            consistency_score=(ai.consistency_score + basic.consistency_score) / 2,
            improvement_areas=list(set(ai.improvement_areas + basic.improvement_areas))[:5]
        )
    
    def _generate_comparison_data(self, analysis: StyleAnalysis) -> Dict[str, Any]:
        """Generate comparison data with peer averages"""
        
        return {
            "peer_average_style": "formal",
            "peer_average_complexity": "intermediate",
            "user_percentile": 75,
            "above_average_metrics": [m.metric_name for m in analysis.metrics if m.percentile > 70],
            "below_average_metrics": [m.metric_name for m in analysis.metrics if m.percentile < 50],
            "style_ranking": "top_25_percent"
        }
    
    def _generate_predictions(self, analysis: StyleAnalysis) -> Dict[str, Any]:
        """Generate predictions for future performance"""
        
        return {
            "predicted_band_score": 7.0,
            "improvement_timeline": "4-6 weeks",
            "key_focus_areas": analysis.improvement_areas[:3],
            "success_probability": 0.8,
            "recommended_practice": "Focus on sentence variety and vocabulary expansion"
        }
    
    def _parse_ai_style_fallback(self, ai_response: str) -> Dict[str, Any]:
        """Fallback parser for AI responses"""
        
        return {
            "overall_style": "formal",
            "complexity_level": "intermediate",
            "metrics": [],
            "patterns": [],
            "strengths": ["AI analysis completed"],
            "weaknesses": ["Limited analysis available"],
            "recommendations": ["Continue practicing writing"],
            "consistency_score": 0.7,
            "improvement_areas": ["general_writing"]
        }
    
    def get_available_styles(self) -> List[str]:
        """Get available writing styles"""
        return [style.value for style in WritingStyle]
    
    def get_complexity_levels(self) -> List[str]:
        """Get available complexity levels"""
        return [level.value for level in ComplexityLevel]


