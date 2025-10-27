"""
Enhanced retrieval system for IELTS writing materials
Uses extracted training data to provide relevant examples and guidance
"""

import os
import json
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class EnhancedIELTSRetriever:
    def __init__(self, knowledge_base_path: str = None):
        self.knowledge_base = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self.load_knowledge_base(knowledge_base_path)
    
    def load_knowledge_base(self, path: str = None):
        """Load the extracted IELTS knowledge base"""
        if path is None:
            # Default path to extracted data
            path = os.path.abspath(os.path.join(
                os.path.dirname(__file__), 
                '..', '..', '..', 'IELTS', 'Writing', 'extracted_training_data', 
                'retrieval_knowledge_base.json'
            ))
        
        if os.path.exists(path):
            with open(path, 'r') as f:
                self.knowledge_base = json.load(f)
            
            # Initialize TF-IDF vectorizer
            if self.knowledge_base:
                self.vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                
                # Create TF-IDF matrix
                texts = [item['content'] for item in self.knowledge_base]
                self.tfidf_matrix = self.vectorizer.fit_transform(texts)
                
                print(f"✅ Loaded {len(self.knowledge_base)} IELTS knowledge base entries")
        else:
            print(f"⚠️ Knowledge base not found at {path}")
    
    def retrieve_relevant_examples(self, query: str, task_type: str = "task2", top_k: int = 3) -> List[Dict]:
        """Retrieve relevant examples based on query and task type"""
        if not self.knowledge_base or not self.vectorizer:
            return []
        
        # Filter by task type
        filtered_items = [
            item for item in self.knowledge_base 
            if item.get('type', '').startswith(task_type)
        ]
        
        if not filtered_items:
            return []
        
        # Get indices of filtered items
        filtered_indices = [
            i for i, item in enumerate(self.knowledge_base) 
            if item.get('type', '').startswith(task_type)
        ]
        
        # Create query vector
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarities for filtered items only
        similarities = cosine_similarity(
            query_vector, 
            self.tfidf_matrix[filtered_indices]
        ).flatten()
        
        # Get top-k most similar items
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Minimum similarity threshold
                item = filtered_items[idx]
                results.append({
                    'content': item['content'],
                    'source': item['source'],
                    'band_score': item.get('band_score', ''),
                    'similarity': float(similarities[idx]),
                    'keywords': item.get('keywords', [])
                })
        
        return results
    
    def get_band_scored_examples(self, band_score: float, task_type: str = "task2", limit: int = 5) -> List[Dict]:
        """Get examples with specific band scores"""
        if not self.knowledge_base:
            return []
        
        # Filter by task type and band score
        filtered_items = [
            item for item in self.knowledge_base 
            if (item.get('type', '').startswith(task_type) and 
                item.get('band_score', '') == str(band_score))
        ]
        
        return filtered_items[:limit]
    
    def get_writing_templates(self, section: str) -> List[str]:
        """Get writing templates for specific essay sections"""
        templates = {
            "introduction": [
                "In today's [context], [topic] has become [impact]. While some argue [opposing view], I believe [position] because [reason 1] and [reason 2].",
                "The issue of [topic] has sparked considerable debate in recent years. Although [opposing view], I maintain that [position] due to [reason 1] and [reason 2].",
                "In the modern world, [topic] presents both opportunities and challenges. While [opposing view], I contend that [position] for [reason 1] and [reason 2]."
            ],
            "topic_sentence": [
                "Firstly, [claim] because [specific reason].",
                "One significant aspect is that [claim] through [specific way].",
                "To begin with, [claim] as evidenced by [specific example].",
                "Moreover, [claim] which can be seen in [specific instance]."
            ],
            "conclusion": [
                "In conclusion, [restate position] because [reason 1] and [reason 2].",
                "To summarize, the evidence clearly shows that [position] due to [reason 1] and [reason 2].",
                "Overall, it is evident that [position] given [reason 1] and [reason 2]."
            ]
        }
        
        return templates.get(section, [])
    
    def get_common_errors_and_fixes(self, band_score: float) -> List[Dict]:
        """Get common errors and fixes based on band score"""
        error_patterns = {
            "5.0-5.5": [
                {
                    "error": "Vague topic sentences",
                    "fix": "Make topic sentences specific and debatable",
                    "example": "Instead of 'Technology is good', write 'Technology improves healthcare accessibility through telemedicine'"
                },
                {
                    "error": "Lack of examples",
                    "fix": "Add concrete, specific examples",
                    "example": "Instead of 'Many people use technology', write 'For instance, 85% of doctors in the UK now use telemedicine platforms'"
                }
            ],
            "6.0-6.5": [
                {
                    "error": "Weak argument development",
                    "fix": "Develop arguments with clear reasoning",
                    "example": "Explain why your example supports your point, don't just state it"
                },
                {
                    "error": "Limited vocabulary range",
                    "fix": "Use more sophisticated vocabulary",
                    "example": "Instead of 'good', use 'beneficial', 'advantageous', 'valuable'"
                }
            ],
            "7.0+": [
                {
                    "error": "Complex sentence errors",
                    "fix": "Ensure complex sentences are grammatically correct",
                    "example": "Use proper subordination and coordination"
                },
                {
                    "error": "Coherence issues",
                    "fix": "Improve paragraph flow and transitions",
                    "example": "Use linking words like 'Furthermore', 'However', 'Consequently'"
                }
            ]
        }
        
        # Find appropriate error patterns based on band score
        if band_score <= 5.5:
            return error_patterns["5.0-5.5"]
        elif band_score <= 6.5:
            return error_patterns["6.0-6.5"]
        else:
            return error_patterns["7.0+"]
    
    def generate_contextual_guidance(self, query: str, current_draft: str = "", task_type: str = "task2") -> Dict:
        """Generate contextual guidance based on query and current draft"""
        # Retrieve relevant examples
        examples = self.retrieve_relevant_examples(query, task_type, top_k=2)
        
        # Get writing templates
        templates = self.get_writing_templates("topic_sentence")
        
        # Analyze current draft for common issues
        guidance = {
            "relevant_examples": examples,
            "templates": templates,
            "suggestions": []
        }
        
        # Add contextual suggestions based on draft analysis
        if current_draft:
            if len(current_draft.split()) < 50:
                guidance["suggestions"].append("Your draft is quite short. Consider adding more detail and examples.")
            if "I think" in current_draft.lower():
                guidance["suggestions"].append("Replace 'I think' with more academic language like 'I believe' or 'I contend'.")
            if current_draft.count('.') < 3:
                guidance["suggestions"].append("Add more specific examples to support your arguments.")
        
        return guidance

# Global instance
enhanced_retriever = EnhancedIELTSRetriever()






