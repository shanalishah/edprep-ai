"""
Advanced ML Scoring Engine for IELTS Writing Assessment
Uses the best trained models with sophisticated error analysis
"""

import pickle
import numpy as np
import pandas as pd
import re
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import logging

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

logger = logging.getLogger(__name__)


class AdvancedMLScoringEngine:
    """
    Advanced ML scoring engine with sophisticated error analysis
    """
    
    def __init__(self, models_dir: str):
        self.models_dir = Path(models_dir)
        self.models = {}
        self.tfidf_vectorizer = None
        self.feature_columns = None
        self.scalers = {}
        self.is_loaded = False
        
        # Error analysis patterns
        self.l1_patterns = self._load_l1_patterns()
        self.interlanguage_patterns = self._load_interlanguage_patterns()
        self.discourse_patterns = self._load_discourse_patterns()
        
        self._load_models()
    
    def _load_l1_patterns(self) -> Dict[str, List[str]]:
        """Load L1-influenced error patterns"""
        return {
            'chinese': [
                r'\b(very much)\b',  # Chinese: hen duo
                r'\b(very good)\b',  # Chinese: hen hao
                r'\b(very big)\b',   # Chinese: hen da
                r'\b(very small)\b', # Chinese: hen xiao
                r'\b(very important)\b', # Chinese: hen zhongyao
            ],
            'arabic': [
                r'\b(the same)\b',   # Arabic: nafs
                r'\b(very much)\b',  # Arabic: kathir
                r'\b(very good)\b',  # Arabic: jayyid jiddan
            ],
            'spanish': [
                r'\b(very much)\b',  # Spanish: mucho
                r'\b(very good)\b',  # Spanish: muy bien
                r'\b(very big)\b',   # Spanish: muy grande
            ],
            'french': [
                r'\b(very much)\b',  # French: beaucoup
                r'\b(very good)\b',  # French: très bien
            ]
        }
    
    def _load_interlanguage_patterns(self) -> Dict[str, List[str]]:
        """Load interlanguage error patterns"""
        return {
            'article_errors': [
                r'\b(go to school)\b',  # Missing article
                r'\b(go to university)\b',
                r'\b(go to hospital)\b',
                r'\b(go to church)\b',
            ],
            'preposition_errors': [
                r'\b(depend of)\b',     # Should be 'depend on'
                r'\b(different of)\b',  # Should be 'different from'
                r'\b(according of)\b',  # Should be 'according to'
            ],
            'tense_errors': [
                r'\b(I am go)\b',       # Present continuous error
                r'\b(I was go)\b',      # Past continuous error
                r'\b(I have go)\b',     # Present perfect error
            ],
            'word_order_errors': [
                r'\b(very much I like)\b',  # Word order
                r'\b(always I go)\b',       # Adverb placement
            ]
        }
    
    def _load_discourse_patterns(self) -> Dict[str, List[str]]:
        """Load discourse management patterns"""
        return {
            'coherence_issues': [
                r'\b(however, but)\b',     # Contradictory connectors
                r'\b(therefore, so)\b',    # Redundant connectors
                r'\b(firstly, first)\b',   # Redundant enumeration
            ],
            'cohesion_issues': [
                r'\b(this)\b(?!\s+(is|was|will|can|should))',  # Vague reference
                r'\b(it)\b(?!\s+(is|was|will|can|should))',    # Vague reference
                r'\b(they)\b(?!\s+(are|were|will|can|should))', # Vague reference
            ],
            'paragraph_structure': [
                r'^[A-Z][^.]*\.$',  # Single sentence paragraphs
            ]
        }
    
    def _load_models(self):
        """Load the best trained ML models"""
        try:
            logger.info("🔄 Loading advanced ML models...")
            
            # Load TF-IDF Vectorizer (try production first, then strict)
            tfidf_path = self.models_dir / "production_tfidf_vectorizer.pkl"
            if not tfidf_path.exists():
                tfidf_path = self.models_dir / "strict_tfidf_vectorizer.pkl"
            
            if tfidf_path.exists():
                with open(tfidf_path, 'rb') as f:
                    self.tfidf_vectorizer = pickle.load(f)
                logger.info("✅ TF-IDF vectorizer loaded")
            
            # Load feature columns (try production first, then strict)
            features_path = self.models_dir / "strict_feature_columns.pkl"
            if features_path.exists():
                with open(features_path, 'rb') as f:
                    self.feature_columns = pickle.load(f)
                logger.info("✅ Feature columns loaded")
            
            # Try to load production models first
            production_models = {
                "Production_Random_Forest_model.pkl": "random_forest",
                "Production_Gradient_Boosting_model.pkl": "gradient_boosting", 
                "Production_Elastic_Net_model.pkl": "elastic_net"
            }
            
            # Load production models
            for model_file, model_type in production_models.items():
                model_path = self.models_dir / model_file
                if model_path.exists():
                    try:
                        with open(model_path, 'rb') as f:
                            model = pickle.load(f)
                        # Store as overall model for now
                        self.models["overall"] = model
                        logger.info(f"✅ Production {model_type} model loaded")
                        break
                    except Exception as e:
                        logger.warning(f"⚠️ Could not load {model_file}: {e}")
            
            # Load production scaler
            scaler_path = self.models_dir / "production_scaler.pkl"
            if scaler_path.exists():
                with open(scaler_path, 'rb') as f:
                    self.scalers["overall"] = pickle.load(f)
                logger.info("✅ Production scaler loaded")
            
            # Check if we have essential components
            if (self.tfidf_vectorizer is not None and 
                self.feature_columns is not None and 
                len(self.models) > 0):
                self.is_loaded = True
                logger.info("✅ Advanced ML models loaded successfully")
            else:
                logger.warning("⚠️ ML models not fully available, will use rule-based fallback")
                self.is_loaded = False
                
        except Exception as e:
            logger.error(f"❌ Error loading ML models: {e}")
            self.is_loaded = False
    
    def is_gibberish_or_low_quality(self, essay: str) -> bool:
        """Advanced gibberish detection with multiple criteria"""
        if not essay or len(essay.strip()) < 10:
            return True
        
        words = re.findall(r'\b\w+\b', essay.lower())
        if len(words) < 10:
            return True
        
        # Check for repeated characters (e.g., "asdasdasd")
        if re.search(r'(.)\1{3,}', essay.lower()):
            return True
        
        # Check for non-English patterns
        non_english_pattern = r'[^a-z\s\.,;\'"-]'
        non_english_chars = len(re.findall(non_english_pattern, essay.lower()))
        if non_english_chars / len(essay) > 0.3:
            return True
        
        # Check for meaningful word ratio
        meaningful_words = [word for word in words if len(word) > 2 and word.isalpha()]
        if len(meaningful_words) / (len(words) + 1e-6) < 0.4:
            return True
        
        # Check for very short sentences
        sentences = sent_tokenize(essay)
        if len(sentences) > 0:
            avg_sentence_length = np.mean([len(sent.split()) for sent in sentences])
            if avg_sentence_length < 3:
                return True
        
        return False
    
    def extract_advanced_features(self, prompt: str, essay: str, task_type: str) -> np.ndarray:
        """Extract comprehensive features for ML prediction"""
        if not essay or pd.isna(essay):
            return self._get_empty_features()
        
        essay = str(essay)
        
        # Basic features
        word_count = len(essay.split())
        char_count = len(essay)
        sentence_count = len(sent_tokenize(essay))
        paragraph_count = len([p for p in essay.split('\n\n') if p.strip()])
        
        # Word-level features
        words = word_tokenize(essay.lower())
        unique_words = len(set(words))
        avg_word_length = np.mean([len(word) for word in words]) if words else 0
        
        # Sentence-level features
        sentences = sent_tokenize(essay)
        avg_sentence_length = np.mean([len(sent.split()) for sent in sentences]) if sentences else 0
        sentence_length_std = np.std([len(sent.split()) for sent in sentences]) if sentences else 0
        
        # Vocabulary features
        lexical_diversity = unique_words / len(words) if words else 0
        
        # Academic vocabulary count
        academic_words = [
            "significant", "substantial", "considerable", "essential", "crucial",
            "fundamental", "important", "vital", "necessary", "critical",
            "moreover", "furthermore", "additionally", "consequently", "therefore",
            "nevertheless", "however", "although", "despite", "whereas",
            "demonstrate", "illustrate", "indicate", "suggest", "reveal",
            "analyze", "evaluate", "assess", "examine", "investigate"
        ]
        academic_word_count = sum(1 for word in academic_words if word in essay.lower())
        
        # Linking words count
        linking_words = [
            "however", "moreover", "furthermore", "therefore", "consequently",
            "nevertheless", "additionally", "similarly", "likewise", "in contrast",
            "on the other hand", "for instance", "for example", "in conclusion",
            "to summarize", "firstly", "secondly", "finally", "meanwhile",
            "as a result", "in addition", "furthermore", "moreover", "besides"
        ]
        linking_word_count = sum(1 for word in linking_words if word in essay.lower())
        
        # Task-specific features
        task_2_indicators = ["I believe", "I think", "in my opinion", "I agree", "I disagree", "I argue"]
        has_opinion = any(indicator in essay.lower() for indicator in task_2_indicators)
        
        # Error analysis features
        l1_errors = self._count_l1_errors(essay)
        interlanguage_errors = self._count_interlanguage_errors(essay)
        discourse_errors = self._count_discourse_errors(essay)
        
        # TF-IDF features
        if self.tfidf_vectorizer:
            try:
                tfidf_features = self.tfidf_vectorizer.transform([essay]).toarray().flatten()
            except:
                tfidf_features = np.zeros(1000)
        else:
            tfidf_features = np.zeros(1000)
        
        # Combine all features
        basic_features = np.array([
            word_count, char_count, sentence_count, paragraph_count,
            unique_words, avg_word_length, avg_sentence_length, sentence_length_std,
            lexical_diversity, academic_word_count, linking_word_count,
            float(has_opinion), float(task_type == "Task 2"),
            l1_errors, interlanguage_errors, discourse_errors
        ])
        
        # For production model, we need to match the expected feature count
        # The production model expects 535 features, so we'll use a subset
        if len(tfidf_features) > 520:
            tfidf_features = tfidf_features[:520]
        elif len(tfidf_features) < 520:
            tfidf_features = np.pad(tfidf_features, (0, 520 - len(tfidf_features)))
        
        combined_features = np.concatenate([basic_features, tfidf_features])
        
        # For production model, we need exactly 535 features
        expected_features = 535
        if len(combined_features) < expected_features:
            combined_features = np.pad(combined_features, (0, expected_features - len(combined_features)))
        elif len(combined_features) > expected_features:
            combined_features = combined_features[:expected_features]
        
        return combined_features.reshape(1, -1)
    
    def _count_l1_errors(self, essay: str) -> int:
        """Count L1-influenced errors"""
        error_count = 0
        for language, patterns in self.l1_patterns.items():
            for pattern in patterns:
                error_count += len(re.findall(pattern, essay.lower()))
        return error_count
    
    def _count_interlanguage_errors(self, essay: str) -> int:
        """Count interlanguage errors"""
        error_count = 0
        for error_type, patterns in self.interlanguage_patterns.items():
            for pattern in patterns:
                error_count += len(re.findall(pattern, essay.lower()))
        return error_count
    
    def _count_discourse_errors(self, essay: str) -> int:
        """Count discourse management errors"""
        error_count = 0
        for error_type, patterns in self.discourse_patterns.items():
            for pattern in patterns:
                error_count += len(re.findall(pattern, essay.lower()))
        return error_count
    
    def _get_empty_features(self) -> np.ndarray:
        """Return empty features array"""
        if self.feature_columns is not None:
            return np.zeros((1, len(self.feature_columns)))
        else:
            return np.zeros((1, 1015))
    
    def score_essay(self, prompt: str, essay: str, task_type: str = "Task 2") -> Dict[str, Any]:
        """Score an essay using advanced ML models with comprehensive analysis"""
        
        # First check for gibberish
        if self.is_gibberish_or_low_quality(essay):
            return {
                "scores": {
                    "task_achievement": 1.0,
                    "coherence_cohesion": 1.0,
                    "lexical_resource": 1.0,
                    "grammatical_range": 1.0,
                    "overall_band_score": 1.0
                },
                "error_analysis": {
                    "l1_errors": 0,
                    "interlanguage_errors": 0,
                    "discourse_errors": 0,
                    "total_errors": 0
                },
                "is_gibberish": True,
                "confidence": 1.0
            }
        
        # Use enhanced rule-based scoring (ML models have poor performance)
        # The production model has negative R² scores, indicating it's not working properly
        logger.warning("⚠️ ML models have poor performance (negative R²), using enhanced rule-based scoring")
        
        # Force use of enhanced rule-based scoring due to ML model quality issues
        return self._score_essay_enhanced_rule_based(prompt, essay, task_type)
    
    def _score_essay_enhanced_rule_based(self, prompt: str, essay: str, task_type: str) -> Dict[str, Any]:
        """Enhanced rule-based scoring with sophisticated analysis"""
        
        # Double-check for gibberish
        if self.is_gibberish_or_low_quality(essay):
            return {
                "scores": {
                    "task_achievement": 1.0,
                    "coherence_cohesion": 1.0,
                    "lexical_resource": 1.0,
                    "grammatical_range": 1.0,
                    "overall_band_score": 1.0
                },
                "error_analysis": {
                    "l1_errors": 0,
                    "interlanguage_errors": 0,
                    "discourse_errors": 0,
                    "total_errors": 0
                },
                "is_gibberish": True,
                "confidence": 1.0,
                "assessment_method": "enhanced_rule_based"
            }
        
        # Enhanced rule-based scoring with more sophisticated analysis
        task_achievement = self._score_task_achievement_enhanced(prompt, essay, task_type)
        coherence_cohesion = self._score_coherence_cohesion_enhanced(essay)
        lexical_resource = self._score_lexical_resource_enhanced(essay)
        grammatical_range = self._score_grammatical_range_enhanced(essay)
        
        overall_band_score = (task_achievement + coherence_cohesion + lexical_resource + grammatical_range) / 4
        
        # Calculate error analysis
        error_analysis = {
            "l1_errors": self._count_l1_errors(essay),
            "interlanguage_errors": self._count_interlanguage_errors(essay),
            "discourse_errors": self._count_discourse_errors(essay),
            "total_errors": 0
        }
        error_analysis["total_errors"] = sum(error_analysis.values())
        
        scores = {
            "task_achievement": round(task_achievement * 2) / 2,
            "coherence_cohesion": round(coherence_cohesion * 2) / 2,
            "lexical_resource": round(lexical_resource * 2) / 2,
            "grammatical_range": round(grammatical_range * 2) / 2,
            "overall_band_score": round(overall_band_score * 2) / 2
        }
        
        # Calculate confidence based on essay quality indicators
        confidence = self._calculate_confidence(essay, scores, error_analysis)
        
        return {
            "scores": scores,
            "error_analysis": error_analysis,
            "is_gibberish": False,
            "confidence": confidence,
            "assessment_method": "enhanced_rule_based"
        }
    
    def _score_essay_rule_based(self, prompt: str, essay: str, task_type: str) -> Dict[str, Any]:
        """Fallback rule-based scoring with advanced analysis"""
        
        # Double-check for gibberish
        if self.is_gibberish_or_low_quality(essay):
            return {
                "scores": {
                    "task_achievement": 1.0,
                    "coherence_cohesion": 1.0,
                    "lexical_resource": 1.0,
                    "grammatical_range": 1.0,
                    "overall_band_score": 1.0
                },
                "error_analysis": {
                    "l1_errors": 0,
                    "interlanguage_errors": 0,
                    "discourse_errors": 0,
                    "total_errors": 0
                },
                "is_gibberish": True,
                "confidence": 1.0
            }
        
        # Advanced rule-based scoring
        task_achievement = self._score_task_achievement_advanced(prompt, essay, task_type)
        coherence_cohesion = self._score_coherence_cohesion_advanced(essay)
        lexical_resource = self._score_lexical_resource_advanced(essay)
        grammatical_range = self._score_grammatical_range_advanced(essay)
        
        overall_band_score = (task_achievement + coherence_cohesion + lexical_resource + grammatical_range) / 4
        
        # Calculate error analysis
        error_analysis = {
            "l1_errors": self._count_l1_errors(essay),
            "interlanguage_errors": self._count_interlanguage_errors(essay),
            "discourse_errors": self._count_discourse_errors(essay),
            "total_errors": 0
        }
        error_analysis["total_errors"] = sum(error_analysis.values())
        
        return {
            "scores": {
                "task_achievement": task_achievement,
                "coherence_cohesion": coherence_cohesion,
                "lexical_resource": lexical_resource,
                "grammatical_range": grammatical_range,
                "overall_band_score": round(overall_band_score * 2) / 2
            },
            "error_analysis": error_analysis,
            "is_gibberish": False,
            "confidence": 0.8  # Rule-based confidence
        }
    
    def _score_task_achievement_enhanced(self, prompt: str, essay: str, task_type: str) -> float:
        """Enhanced task achievement scoring with more sophisticated analysis"""
        word_count = len(essay.split())
        score = 1.0  # Start very low
        
        # Word count requirements (strict)
        if task_type == "Task 2":
            if word_count >= 250:
                score += 3.0  # Increased weight
            elif word_count >= 200:
                score += 2.0
            elif word_count >= 150:
                score += 1.0
            else:
                return 1.0
        else:  # Task 1
            if word_count >= 150:
                score += 3.0
            elif word_count >= 100:
                score += 2.0
            elif word_count >= 75:
                score += 1.0
            else:
                return 1.0
        
        # Check for clear position/opinion (Task 2) - more sophisticated
        if task_type == "Task 2":
            opinion_indicators = ["I believe", "I think", "in my opinion", "I agree", "I disagree", "I argue", "I maintain", "I support", "I oppose", "I favor", "I prefer"]
            strong_opinion_indicators = ["I strongly believe", "I firmly believe", "I completely agree", "I strongly disagree", "I absolutely support"]
            
            if any(indicator in essay.lower() for indicator in strong_opinion_indicators):
                score += 1.5  # Higher score for strong opinions
            elif any(indicator in essay.lower() for indicator in opinion_indicators):
                score += 1.0
        
        # Check for examples and evidence - more comprehensive
        example_indicators = ["for example", "for instance", "such as", "like", "including", "specifically", "particularly", "notably", "especially"]
        evidence_indicators = ["research shows", "studies indicate", "statistics reveal", "data suggests", "evidence shows", "findings demonstrate"]
        
        example_count = sum(1 for indicator in example_indicators if indicator in essay.lower())
        evidence_count = sum(1 for indicator in evidence_indicators if indicator in essay.lower())
        
        score += min(2.0, example_count * 0.5 + evidence_count * 0.8)  # Cap at 2.0
        
        # Check for conclusion - more sophisticated
        conclusion_indicators = ["in conclusion", "to conclude", "to sum up", "overall", "in summary", "finally", "ultimately", "in the end", "to summarize"]
        if any(indicator in essay.lower() for indicator in conclusion_indicators):
            score += 1.0
        
        # Check for addressing both sides (for discussion essays)
        if "discuss" in prompt.lower():
            both_sides_indicators = ["on the one hand", "on the other hand", "however", "nevertheless", "although", "despite", "whereas", "while"]
            if any(indicator in essay.lower() for indicator in both_sides_indicators):
                score += 1.0
        
        # Check for task-specific requirements
        if "advantages" in prompt.lower() and "disadvantages" in prompt.lower():
            if "advantage" in essay.lower() and "disadvantage" in essay.lower():
                score += 1.0
        
        return min(9.0, score)
    
    def _score_coherence_cohesion_enhanced(self, essay: str) -> float:
        """Enhanced coherence and cohesion scoring"""
        score = 1.0
        
        # Paragraph structure
        paragraphs = [p.strip() for p in essay.split('\n\n') if p.strip()]
        if len(paragraphs) >= 3:  # Introduction, body, conclusion
            score += 2.0
        elif len(paragraphs) >= 2:
            score += 1.0
        
        # Linking words and cohesive devices
        linking_words = [
            "however", "therefore", "moreover", "furthermore", "additionally", "consequently",
            "nevertheless", "meanwhile", "similarly", "likewise", "in contrast", "on the other hand",
            "for example", "for instance", "such as", "in conclusion", "to summarize", "firstly",
            "secondly", "finally", "as a result", "in addition", "besides", "although", "despite",
            "whereas", "while", "since", "because", "due to", "owing to"
        ]
        
        linking_count = sum(1 for word in linking_words if word in essay.lower())
        score += min(2.0, linking_count * 0.3)  # Cap at 2.0
        
        # Logical flow indicators
        flow_indicators = ["first", "second", "third", "next", "then", "after", "before", "initially", "subsequently", "ultimately"]
        flow_count = sum(1 for word in flow_indicators if word in essay.lower())
        score += min(1.0, flow_count * 0.2)  # Cap at 1.0
        
        # Cohesive devices (pronouns, demonstratives)
        cohesive_devices = ["this", "that", "these", "those", "it", "they", "them", "their", "its", "which", "who", "whom"]
        cohesive_count = sum(1 for word in cohesive_devices if word in essay.lower())
        score += min(1.0, cohesive_count * 0.1)  # Cap at 1.0
        
        return min(9.0, score)
    
    def _score_lexical_resource_enhanced(self, essay: str) -> float:
        """Enhanced lexical resource scoring"""
        score = 1.0
        
        words = essay.lower().split()
        unique_words = set(words)
        
        # Vocabulary range
        lexical_diversity = len(unique_words) / len(words) if words else 0
        if lexical_diversity > 0.7:
            score += 2.0
        elif lexical_diversity > 0.6:
            score += 1.5
        elif lexical_diversity > 0.5:
            score += 1.0
        
        # Academic vocabulary
        academic_words = [
            "significant", "substantial", "considerable", "essential", "crucial", "fundamental",
            "important", "vital", "necessary", "critical", "moreover", "furthermore", "additionally",
            "consequently", "therefore", "nevertheless", "however", "although", "despite", "whereas",
            "demonstrate", "illustrate", "indicate", "suggest", "reveal", "analyze", "evaluate",
            "assess", "examine", "investigate", "comprehensive", "extensive", "profound", "remarkable",
            "outstanding", "exceptional", "notable", "prominent", "distinguished", "sophisticated"
        ]
        
        academic_count = sum(1 for word in academic_words if word in essay.lower())
        score += min(2.0, academic_count * 0.3)  # Cap at 2.0
        
        # Word choice precision
        precise_words = [
            "exactly", "precisely", "specifically", "particularly", "especially", "notably",
            "remarkably", "significantly", "substantially", "considerably", "dramatically",
            "tremendously", "enormously", "vastly", "greatly", "immensely"
        ]
        
        precise_count = sum(1 for word in precise_words if word in essay.lower())
        score += min(1.0, precise_count * 0.2)  # Cap at 1.0
        
        # Collocations and natural expressions
        natural_expressions = [
            "make a difference", "play a role", "have an impact", "take into account",
            "in terms of", "as a result of", "due to the fact", "it is worth noting",
            "it should be noted", "it is important to", "it is essential to"
        ]
        
        natural_count = sum(1 for expr in natural_expressions if expr in essay.lower())
        score += min(1.0, natural_count * 0.5)  # Cap at 1.0
        
        return min(9.0, score)
    
    def _score_grammatical_range_enhanced(self, essay: str) -> float:
        """Enhanced grammatical range and accuracy scoring"""
        score = 1.0
        
        sentences = sent_tokenize(essay)
        
        # Sentence variety
        simple_sentences = 0
        compound_sentences = 0
        complex_sentences = 0
        
        for sentence in sentences:
            if ',' in sentence and any(conj in sentence.lower() for conj in ['and', 'but', 'or', 'so', 'yet']):
                compound_sentences += 1
            elif any(subord in sentence.lower() for subord in ['because', 'although', 'while', 'since', 'if', 'when', 'where', 'which', 'who', 'that']):
                complex_sentences += 1
            else:
                simple_sentences += 1
        
        total_sentences = len(sentences)
        if total_sentences > 0:
            variety_score = (compound_sentences + complex_sentences) / total_sentences
            score += variety_score * 2.0  # Up to 2.0 points for variety
        
        # Tense consistency
        present_tense_verbs = len(re.findall(r'\b(am|is|are|was|were|be|being|been|have|has|had|do|does|did|will|would|can|could|may|might|must|should|shall)\b', essay.lower()))
        if present_tense_verbs > 0:
            score += 1.0
        
        # Complex grammatical structures
        complex_structures = [
            r'\b(not only.*but also)\b',  # Not only...but also
            r'\b(so.*that)\b',  # So...that
            r'\b(such.*that)\b',  # Such...that
            r'\b(the more.*the more)\b',  # The more...the more
            r'\b(no sooner.*than)\b',  # No sooner...than
            r'\b(hardly.*when)\b',  # Hardly...when
        ]
        
        complex_count = sum(len(re.findall(pattern, essay.lower())) for pattern in complex_structures)
        score += min(1.0, complex_count * 0.5)  # Cap at 1.0
        
        # Passive voice usage
        passive_voice = len(re.findall(r'\b(am|is|are|was|were|be|being|been)\s+\w+ed\b', essay.lower()))
        if passive_voice > 0:
            score += 0.5
        
        # Conditional sentences
        conditionals = len(re.findall(r'\b(if|unless|provided that|as long as)\b', essay.lower()))
        score += min(1.0, conditionals * 0.3)  # Cap at 1.0
        
        return min(9.0, score)
    
    def _calculate_confidence(self, essay: str, scores: dict, error_analysis: dict) -> float:
        """Calculate confidence based on essay quality indicators"""
        confidence = 0.8  # Base confidence
        
        # Adjust based on essay length
        word_count = len(essay.split())
        if word_count >= 250:
            confidence += 0.1
        elif word_count < 150:
            confidence -= 0.1
        
        # Adjust based on error count
        total_errors = error_analysis.get("total_errors", 0)
        if total_errors == 0:
            confidence += 0.05
        elif total_errors > 10:
            confidence -= 0.1
        
        # Adjust based on score consistency
        score_values = list(scores.values())
        if len(set(score_values)) == 1:  # All scores the same
            confidence -= 0.05
        
        return min(0.95, max(0.7, confidence))
    
    def _score_task_achievement_advanced(self, prompt: str, essay: str, task_type: str) -> float:
        """Advanced task achievement scoring"""
        word_count = len(essay.split())
        score = 1.0  # Start very low
        
        # Word count requirements (strict)
        if task_type == "Task 2":
            if word_count >= 250:
                score += 2.5
            elif word_count >= 200:
                score += 1.5
            elif word_count >= 150:
                score += 0.5
            else:
                return 1.0
        else:  # Task 1
            if word_count >= 150:
                score += 2.5
            elif word_count >= 100:
                score += 1.5
            elif word_count >= 75:
                score += 0.5
            else:
                return 1.0
        
        # Check for clear position/opinion (Task 2)
        if task_type == "Task 2":
            opinion_indicators = ["I believe", "I think", "in my opinion", "I agree", "I disagree", "I argue", "I maintain"]
            if any(indicator in essay.lower() for indicator in opinion_indicators):
                score += 1.0
        
        # Check for examples and evidence
        example_indicators = ["for example", "for instance", "such as", "like", "including", "specifically"]
        if any(indicator in essay.lower() for indicator in example_indicators):
            score += 1.0
        
        # Check for conclusion
        conclusion_indicators = ["in conclusion", "to conclude", "to sum up", "overall", "in summary", "finally"]
        if any(indicator in essay.lower() for indicator in conclusion_indicators):
            score += 1.0
        
        # Check for addressing both sides (for discussion essays)
        if "discuss" in prompt.lower():
            both_sides_indicators = ["on one hand", "on the other hand", "however", "nevertheless", "although"]
            if sum(1 for indicator in both_sides_indicators if indicator in essay.lower()) >= 2:
                score += 1.0
        
        return min(9.0, max(1.0, score))
    
    def _score_coherence_cohesion_advanced(self, essay: str) -> float:
        """Advanced coherence and cohesion scoring"""
        score = 1.0  # Start very low
        
        # Check paragraph structure
        paragraphs = essay.split('\n\n')
        if len(paragraphs) >= 4:  # Introduction, 2 body paragraphs, conclusion
            score += 2.0
        elif len(paragraphs) >= 3:
            score += 1.0
        
        # Check for linking words (comprehensive)
        linking_words = [
            "however", "therefore", "moreover", "furthermore", "additionally",
            "on the other hand", "in contrast", "similarly", "likewise",
            "firstly", "secondly", "finally", "in addition", "as a result",
            "consequently", "nevertheless", "meanwhile", "subsequently"
        ]
        
        linking_count = sum(1 for word in linking_words if word in essay.lower())
        if linking_count >= 6:
            score += 2.0
        elif linking_count >= 4:
            score += 1.5
        elif linking_count >= 2:
            score += 1.0
        
        # Check for sentence variety
        sentences = essay.split('.')
        if len(sentences) >= 10:
            score += 1.0
        
        # Check for topic sentences
        topic_sentence_indicators = ["first", "second", "third", "another", "furthermore", "moreover"]
        topic_sentences = sum(1 for indicator in topic_sentence_indicators if indicator in essay.lower())
        if topic_sentences >= 2:
            score += 1.0
        
        return min(9.0, max(1.0, score))
    
    def _score_lexical_resource_advanced(self, essay: str) -> float:
        """Advanced lexical resource scoring"""
        score = 1.0  # Start very low
        
        # Calculate vocabulary diversity
        words = essay.lower().split()
        unique_words = set(words)
        if len(words) > 0:
            diversity = len(unique_words) / len(words)
            if diversity > 0.8:
                score += 2.5
            elif diversity > 0.7:
                score += 2.0
            elif diversity > 0.6:
                score += 1.5
            elif diversity > 0.5:
                score += 1.0
        
        # Check for academic vocabulary
        academic_words = [
            "significant", "substantial", "considerable", "essential", "crucial",
            "fundamental", "important", "vital", "necessary", "critical",
            "moreover", "furthermore", "additionally", "consequently", "therefore",
            "demonstrate", "illustrate", "indicate", "suggest", "reveal",
            "analyze", "evaluate", "assess", "examine", "investigate"
        ]
        academic_count = sum(1 for word in academic_words if word in essay.lower())
        if academic_count >= 8:
            score += 2.0
        elif academic_count >= 5:
            score += 1.5
        elif academic_count >= 3:
            score += 1.0
        
        # Check for word length variety
        long_words = [word for word in words if len(word) > 7]
        if len(long_words) / len(words) > 0.2:
            score += 1.0
        elif len(long_words) / len(words) > 0.15:
            score += 0.5
        
        # Check for collocations
        collocations = [
            "make a decision", "take into account", "play a role", "have an impact",
            "bring about", "carry out", "set up", "put forward"
        ]
        collocation_count = sum(1 for collocation in collocations if collocation in essay.lower())
        if collocation_count >= 2:
            score += 1.0
        
        return min(9.0, max(1.0, score))
    
    def _score_grammatical_range_advanced(self, essay: str) -> float:
        """Advanced grammatical range scoring"""
        score = 1.0  # Start very low
        
        # Check for sentence variety
        sentences = essay.split('.')
        if len(sentences) >= 10:
            score += 1.5
        elif len(sentences) >= 8:
            score += 1.0
        
        # Check for complex sentences
        complex_indicators = ["although", "because", "since", "while", "whereas", "if", "unless", "provided that"]
        complex_count = sum(1 for indicator in complex_indicators if indicator in essay.lower())
        if complex_count >= 4:
            score += 2.0
        elif complex_count >= 2:
            score += 1.5
        elif complex_count >= 1:
            score += 1.0
        
        # Check for passive voice
        passive_indicators = ["is", "are", "was", "were", "been", "being"]
        passive_count = sum(1 for indicator in passive_indicators if indicator in essay.lower())
        if passive_count >= 4:
            score += 1.0
        
        # Check for different tenses
        tense_indicators = ["will", "would", "has", "have", "had", "can", "could", "should", "might", "may"]
        tense_count = sum(1 for indicator in tense_indicators if indicator in essay.lower())
        if tense_count >= 5:
            score += 1.5
        elif tense_count >= 3:
            score += 1.0
        
        # Check for conditional sentences
        conditional_indicators = ["if", "unless", "provided that", "as long as"]
        conditional_count = sum(1 for indicator in conditional_indicators if indicator in essay.lower())
        if conditional_count >= 2:
            score += 1.0
        
        # Check for relative clauses
        relative_indicators = ["which", "that", "who", "whom", "whose", "where", "when"]
        relative_count = sum(1 for indicator in relative_indicators if indicator in essay.lower())
        if relative_count >= 3:
            score += 1.0
        
        return min(9.0, max(1.0, score))
