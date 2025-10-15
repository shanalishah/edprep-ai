#!/usr/bin/env python3
"""
Test script for the hybrid scoring engine
Demonstrates the difference between rule-based and LLM-powered scoring
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.services.hybrid_scoring_engine import HybridScoringEngine
from app.services.ml_scoring_engine import AdvancedMLScoringEngine

def test_scoring_engines():
    """Test and compare different scoring approaches"""
    
    # Test essays of different qualities
    test_essays = [
        {
            "name": "Basic Essay",
            "prompt": "Some people think that technology has made our lives more complicated. What is your opinion?",
            "essay": "Technology has definitely made our lives more complicated in many ways. For example, we now have to learn how to use smartphones, computers, and various apps. However, technology has also made many things easier, such as communication and access to information. In my opinion, the benefits outweigh the drawbacks.",
            "task_type": "Task 2"
        },
        {
            "name": "Advanced Essay", 
            "prompt": "Some people think that technology has made our lives more complicated. What is your opinion?",
            "essay": "I completely disagree with the statement that technology has made our lives more complicated. In fact, I believe that technology has significantly simplified our daily routines and improved our quality of life. For instance, online banking allows us to manage our finances from home, eliminating the need to visit physical branches. Similarly, GPS navigation systems have made travel much easier by providing real-time directions and traffic updates. Furthermore, communication has been revolutionized through social media platforms and video calling applications, enabling us to stay connected with friends and family regardless of distance. While it is true that we need to learn how to use new devices and applications, the long-term benefits far outweigh the initial learning curve. In conclusion, technology has made our lives more convenient and efficient rather than more complicated.",
            "task_type": "Task 2"
        },
        {
            "name": "Poor Essay",
            "prompt": "Some people think that technology has made our lives more complicated. What is your opinion?",
            "essay": "Technology bad. Life hard. No good. Bad grammar and spelling erors everywhere. No examples or evidence. Just random thoughts. Technology bad. Life hard. No conclusion. Random words. Bad writing. Terrible essay. No organization. Poor vocabulary. Grammar mistakes. Spelling errors. No coherence. Bad structure. Terrible writing. Awful essay. No examples. No evidence. No support. Bad arguments. Poor reasoning. No support. Terrible conclusion. Bad organization. Poor flow. Awful writing. No structure. Bad coherence. Grammar errors. Spelling mistakes. Terrible vocabulary. No examples. No evidence. Bad arguments. Poor reasoning. No support. Terrible conclusion.",
            "task_type": "Task 2"
        }
    ]
    
    # Initialize engines
    models_dir = "/Users/shan/Desktop/Work/Projects/EdPrep AI/ielts-master-platform/backend/models"
    
    print("🔄 Initializing scoring engines...")
    
    # Rule-based engine (current system)
    rule_engine = AdvancedMLScoringEngine(models_dir)
    print("✅ Rule-based engine initialized")
    
    # Hybrid engine (without LLM for now)
    hybrid_engine = HybridScoringEngine(
        models_dir=models_dir,
        openai_api_key=None,  # No API key for this test
        anthropic_api_key=None
    )
    print("✅ Hybrid engine initialized (rule-based mode)")
    
    print("\n" + "="*80)
    print("📊 SCORING COMPARISON RESULTS")
    print("="*80)
    
    for i, test_case in enumerate(test_essays, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print("-" * 50)
        
        # Rule-based scoring
        rule_result = rule_engine.score_essay(
            test_case["prompt"], 
            test_case["essay"], 
            test_case["task_type"]
        )
        
        # Hybrid scoring (will fall back to rule-based without LLM)
        hybrid_result = hybrid_engine.score_essay(
            test_case["prompt"], 
            test_case["essay"], 
            test_case["task_type"]
        )
        
        print(f"📊 Rule-based Scores:")
        for criterion, score in rule_result["scores"].items():
            print(f"   {criterion.replace('_', ' ').title()}: {score}")
        print(f"   Assessment Method: {rule_result.get('assessment_method', 'unknown')}")
        print(f"   Confidence: {rule_result.get('confidence', 0.8):.2f}")
        
        print(f"\n🤖 Hybrid Scores:")
        for criterion, score in hybrid_result["scores"].items():
            print(f"   {criterion.replace('_', ' ').title()}: {score}")
        print(f"   Assessment Method: {hybrid_result.get('assessment_method', 'unknown')}")
        print(f"   Confidence: {hybrid_result.get('confidence', 0.8):.2f}")
        
        # Show component scores if available
        if "component_scores" in hybrid_result:
            print(f"\n🔍 Component Scores:")
            print(f"   Rule-based: {hybrid_result['component_scores']['rule_based']}")
            print(f"   LLM-based: {hybrid_result['component_scores']['llm_based']}")
    
    print("\n" + "="*80)
    print("💡 RECOMMENDATIONS")
    print("="*80)
    print("1. 🔑 Add OpenAI or Anthropic API keys to enable LLM-powered scoring")
    print("2. 📈 LLM scoring will provide more nuanced and accurate assessments")
    print("3. 🛡️ Hybrid approach ensures fallback to rule-based if LLM fails")
    print("4. 💰 Monitor LLM usage costs and implement rate limiting")
    print("5. 🎯 Consider fine-tuning prompts for better IELTS-specific scoring")
    
    print("\n🚀 To enable LLM scoring:")
    print("   export OPENAI_API_KEY='your-api-key-here'")
    print("   # OR")
    print("   export ANTHROPIC_API_KEY='your-api-key-here'")

if __name__ == "__main__":
    test_scoring_engines()
