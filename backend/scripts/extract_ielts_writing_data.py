#!/usr/bin/env python3
"""
Extract and organize IELTS writing tasks and examples from all available sources
for training the Writing Coach agents.
"""

import os
import json
import csv
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
import re

def extract_from_csv_datasets():
    """Extract writing tasks and examples from CSV datasets"""
    data_dir = Path("../../IELTS/Writing/data_writing")
    extracted_data = {
        "task1_examples": [],
        "task2_examples": [],
        "band_scored_essays": []
    }
    
    # Main writing dataset
    main_dataset = data_dir / "ielts_writing_dataset.csv"
    if main_dataset.exists():
        print(f"📊 Processing {main_dataset.name}...")
        df = pd.read_csv(main_dataset)
        
        for _, row in df.iterrows():
            task_type = row.get('Task_Type', '')
            question = row.get('Question', '')
            essay = row.get('Essay', '')
            overall_score = row.get('Overall', '')
            
            if task_type == 1 and question and essay:
                extracted_data["task1_examples"].append({
                    "prompt": question,
                    "response": essay,
                    "band_score": overall_score,
                    "source": "ielts_writing_dataset.csv"
                })
            elif task_type == 2 and question and essay:
                extracted_data["task2_examples"].append({
                    "prompt": question,
                    "response": essay,
                    "band_score": overall_score,
                    "source": "ielts_writing_dataset.csv"
                })
    
    # Human feedback dataset
    feedback_dataset = data_dir / "human_feedback_ielts_writing.csv"
    if feedback_dataset.exists():
        print(f"📊 Processing {feedback_dataset.name}...")
        try:
            df = pd.read_csv(feedback_dataset)
            for _, row in df.iterrows():
                if 'prompt' in df.columns and 'response' in df.columns:
                    extracted_data["band_scored_essays"].append({
                        "prompt": row.get('prompt', ''),
                        "response": row.get('response', ''),
                        "feedback": row.get('feedback', ''),
                        "source": "human_feedback_ielts_writing.csv"
                    })
        except Exception as e:
            print(f"⚠️ Error processing feedback dataset: {e}")
    
    return extracted_data

def extract_from_cambridge_pdfs():
    """Extract writing tasks from Cambridge IELTS PDFs"""
    # This would require PDF parsing - for now, return structure
    return {
        "cambridge_tasks": [],
        "official_examples": [],
        "band_descriptors": []
    }

def create_training_prompts(extracted_data: Dict) -> Dict[str, List[str]]:
    """Create training prompts for each agent role based on extracted data"""
    
    training_prompts = {
        "questioner_examples": [],
        "explainer_examples": [],
        "challenger_examples": []
    }
    
    # Generate Questioner examples
    for task in extracted_data["task2_examples"][:10]:  # Sample first 10
        prompt = task["prompt"]
        response = task["response"]
        band_score = task.get("band_score", "")
        
        questioner_example = f"""
Task: {prompt}
Student Response: {response[:200]}...
Band Score: {band_score}

Questioner Guidance:
"What specific examples can you provide to support your main argument? Use this template: 'For instance, [specific example] demonstrates [your point] because [explanation].' Now write one concrete example for your first body paragraph."
"""
        training_prompts["questioner_examples"].append(questioner_example)
    
    # Generate Explainer examples
    for task in extracted_data["task2_examples"][:10]:
        prompt = task["prompt"]
        response = task["response"]
        band_score = task.get("band_score", "")
        
        explainer_example = f"""
Task: {prompt}
Student Response: {response[:200]}...
Band Score: {band_score}

Explainer Guidance:
"Rule: Topic sentences should state a clear claim. Example: 'Technology has improved healthcare accessibility through telemedicine.' Now write your Body 1 topic sentence using this pattern: '[Your claim] + [specific way/example].'"
"""
        training_prompts["explainer_examples"].append(explainer_example)
    
    # Generate Challenger examples
    for task in extracted_data["task2_examples"][:10]:
        prompt = task["prompt"]
        response = task["response"]
        band_score = task.get("band_score", "")
        
        challenger_example = f"""
Task: {prompt}
Student Response: {response[:200]}...
Band Score: {band_score}

Challenger Guidance:
"Your introduction lacks specificity. Rewrite it using this structure: 'In [context], [topic] has [impact]. While [opposing view], I believe [position] because [reason 1] and [reason 2].' Make your position more debatable and your reasons more distinct."
"""
        training_prompts["challenger_examples"].append(challenger_example)
    
    return training_prompts

def create_retrieval_knowledge_base(extracted_data: Dict) -> List[Dict]:
    """Create knowledge base for retrieval system"""
    knowledge_base = []
    
    # Add Task 2 prompts and responses
    for task in extracted_data["task2_examples"]:
        knowledge_base.append({
            "content": f"Task 2 Prompt: {task['prompt']}\n\nSample Response: {task['response'][:500]}...",
            "source": task["source"],
            "type": "task2_example",
            "band_score": task.get("band_score", ""),
            "keywords": extract_keywords(task["prompt"])
        })
    
    # Add Task 1 examples
    for task in extracted_data["task1_examples"]:
        knowledge_base.append({
            "content": f"Task 1 Prompt: {task['prompt']}\n\nSample Response: {task['response'][:500]}...",
            "source": task["source"],
            "type": "task1_example",
            "band_score": task.get("band_score", ""),
            "keywords": extract_keywords(task["prompt"])
        })
    
    return knowledge_base

def extract_keywords(text: str) -> List[str]:
    """Extract keywords from text for better retrieval"""
    # Simple keyword extraction
    keywords = []
    common_words = ["the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"]
    
    words = re.findall(r'\b\w+\b', text.lower())
    for word in words:
        if len(word) > 3 and word not in common_words:
            keywords.append(word)
    
    return list(set(keywords))[:10]  # Top 10 unique keywords

def main():
    """Main extraction function"""
    print("🚀 Starting IELTS Writing Data Extraction...")
    
    # Extract from CSV datasets
    extracted_data = extract_from_csv_datasets()
    
    print(f"✅ Extracted {len(extracted_data['task1_examples'])} Task 1 examples")
    print(f"✅ Extracted {len(extracted_data['task2_examples'])} Task 2 examples")
    print(f"✅ Extracted {len(extracted_data['band_scored_essays'])} band-scored essays")
    
    # Create training prompts
    training_prompts = create_training_prompts(extracted_data)
    
    # Create knowledge base
    knowledge_base = create_retrieval_knowledge_base(extracted_data)
    
    # Save results
    output_dir = Path("../../IELTS/Writing/extracted_training_data")
    output_dir.mkdir(exist_ok=True)
    
    # Save extracted data
    with open(output_dir / "extracted_writing_data.json", "w") as f:
        json.dump(extracted_data, f, indent=2)
    
    # Save training prompts
    with open(output_dir / "agent_training_prompts.json", "w") as f:
        json.dump(training_prompts, f, indent=2)
    
    # Save knowledge base
    with open(output_dir / "retrieval_knowledge_base.json", "w") as f:
        json.dump(knowledge_base, f, indent=2)
    
    print(f"💾 Saved extracted data to {output_dir}")
    print(f"📚 Created {len(knowledge_base)} knowledge base entries")
    print(f"🎯 Generated training examples for all agent roles")
    
    return extracted_data, training_prompts, knowledge_base

if __name__ == "__main__":
    main()




