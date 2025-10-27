import os
import json
import glob
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class TestDataService:
    def __init__(self):
        # Path to the Archive test data - use relative path for deployment
        if os.path.exists("/Users/shan/Desktop/Work/Projects/EdPrep AI/ARCHIVE/test-data/IELTS"):
            # Local development
            self.archive_path = Path("/Users/shan/Desktop/Work/Projects/EdPrep AI/ARCHIVE/test-data/IELTS")
        else:
            # Production deployment - use data directory
            self.archive_path = Path("data")
        
        self.cambridge_path = self.archive_path / "Cambridge IELTS"
        self.speaking_data_path = self.archive_path / "Speaking" / "data_speaking"
        self.writing_data_path = self.archive_path / "Writing" / "data_writing"
        
    def get_listening_tests(self) -> List[Dict[str, Any]]:
        """Get all available listening tests with audio files"""
        listening_tests = []
        
        # Scan Academic tests
        academic_path = self.cambridge_path / "Academic"
        for test_book in academic_path.iterdir():
            if test_book.is_dir() and "Cambridge IELTS" in test_book.name:
                book_name = test_book.name
                book_number = self._extract_book_number(book_name)
                
                # Find all test directories
                for test_dir in test_book.iterdir():
                    if test_dir.is_dir() and test_dir.name.startswith("test"):
                        test_number = test_dir.name.replace("test", "")
                        
                        # Find audio files
                        audio_files = list(test_dir.glob("*.mp3"))
                        if audio_files:
                            sections = []
                            for audio_file in sorted(audio_files):
                                section_name = audio_file.stem
                                # Create relative path for serving via API
                                relative_path = audio_file.relative_to(self.archive_path)
                                sections.append({
                                    "section": section_name,
                                    "audio_file": f"/api/v1/audio/{relative_path}",
                                    "duration": "~10 minutes"  # Estimated
                                })
                            
                            listening_tests.append({
                                "id": f"listening_{book_number}_{test_number}",
                                "title": f"Cambridge IELTS {book_number} - Test {test_number}",
                                "book": book_number,
                                "test_number": test_number,
                                "type": "Academic",
                                "difficulty": self._get_difficulty_by_book(book_number),
                                "estimated_time": "40 minutes",
                                "sections": sections,
                                "description": f"Complete IELTS Listening test from Cambridge IELTS {book_number}",
                                "total_sections": len(sections)
                            })
        
        return listening_tests
    
    def get_reading_tests(self) -> List[Dict[str, Any]]:
        """Get all available reading tests"""
        reading_tests = []
        
        # Scan Academic tests
        academic_path = self.cambridge_path / "Academic"
        for test_book in academic_path.iterdir():
            if test_book.is_dir() and "Cambridge IELTS" in test_book.name:
                book_name = test_book.name
                book_number = self._extract_book_number(book_name)
                
                # Find PDF files
                pdf_files = list(test_book.glob("*.pdf"))
                if pdf_files:
                    reading_tests.append({
                        "id": f"reading_{book_number}",
                        "title": f"Cambridge IELTS {book_number} - Reading Tests",
                        "book": book_number,
                        "type": "Academic",
                        "difficulty": self._get_difficulty_by_book(book_number),
                        "estimated_time": "60 minutes",
                        "pdf_file": str(pdf_files[0]),
                        "description": f"Complete IELTS Reading tests from Cambridge IELTS {book_number}",
                        "total_passages": 3,
                        "total_questions": 40
                    })
        
        # Add General Training tests
        general_path = self.cambridge_path / "General"
        for pdf_file in general_path.glob("*.pdf"):
            if "Cambridge IELTS" in pdf_file.name:
                book_number = self._extract_book_number(pdf_file.name)
                reading_tests.append({
                    "id": f"reading_gt_{book_number}",
                    "title": f"Cambridge IELTS {book_number} GT - Reading Tests",
                    "book": book_number,
                    "type": "General Training",
                    "difficulty": self._get_difficulty_by_book(book_number),
                    "estimated_time": "60 minutes",
                    "pdf_file": str(pdf_file),
                    "description": f"Complete IELTS General Training Reading tests from Cambridge IELTS {book_number}",
                    "total_passages": 3,
                    "total_questions": 40
                })
        
        return reading_tests
    
    def get_speaking_tests(self) -> List[Dict[str, Any]]:
        """Get all available speaking tests from JSON data"""
        speaking_tests = []
        
        # Load speaking data
        speaking_files = [
            self.speaking_data_path / "ielts_new.json",
            self.speaking_data_path / "ielts_old.json"
        ]
        
        for file_path in speaking_files:
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Group questions by topic/theme
                    topics = self._group_speaking_questions(data)
                    
                    for topic, questions in topics.items():
                        # Limit questions to avoid overwhelming the API response
                        limited_questions = questions[:10] if len(questions) > 10 else questions
                        
                        speaking_tests.append({
                            "id": f"speaking_{file_path.stem}_{topic.lower().replace(' ', '_')}",
                            "title": f"Speaking Practice - {topic}",
                            "type": "Speaking",
                            "topic": topic,
                            "difficulty": "Mixed",
                            "estimated_time": "15 minutes",
                            "questions": limited_questions,
                            "description": f"Practice speaking about {topic.lower()} with common IELTS questions",
                            "total_questions": len(limited_questions)
                        })
                        
                except Exception as e:
                    logger.error(f"Error loading speaking data from {file_path}: {e}")
                    # Add fallback speaking tests if file loading fails
                    speaking_tests.extend(self._get_fallback_speaking_tests())
        
        # If no tests were loaded, add fallback tests
        if not speaking_tests:
            speaking_tests.extend(self._get_fallback_speaking_tests())
        
        return speaking_tests
    
    def get_writing_tests(self) -> List[Dict[str, Any]]:
        """Get all available writing tests"""
        writing_tests = []
        
        # Real IELTS Writing Task 2 prompts from Cambridge IELTS
        real_prompts = [
            {
                "prompt": "Some people believe that technology has made our lives more complicated, while others think it has made life easier. Discuss both views and give your opinion.",
                "topic": "Technology",
                "task_type": "Task 2",
                "difficulty": "Medium"
            },
            {
                "prompt": "Some people think that formal education is more important than practical experience. Others believe that practical experience is more valuable. Discuss both views and give your opinion.",
                "topic": "Education",
                "task_type": "Task 2",
                "difficulty": "Easy"
            },
            {
                "prompt": "Environmental problems are becoming increasingly serious. What are the main causes of these problems? What measures can be taken to address them?",
                "topic": "Environment",
                "task_type": "Task 2",
                "difficulty": "Hard"
            },
            {
                "prompt": "In many countries, people are working longer hours than ever before. What are the causes of this trend? What effects does it have on individuals and society?",
                "topic": "Work",
                "task_type": "Task 2",
                "difficulty": "Medium"
            },
            {
                "prompt": "Some people believe that the best way to reduce crime is to give longer prison sentences. Others, however, think there are better ways to reduce crime. Discuss both views and give your opinion.",
                "topic": "Society",
                "task_type": "Task 2",
                "difficulty": "Hard"
            },
            {
                "prompt": "The chart below shows the energy consumption in different countries from 2000 to 2010. Summarize the information by selecting and reporting the main features, and make comparisons where relevant.",
                "topic": "Data Analysis",
                "task_type": "Task 1",
                "difficulty": "Medium"
            },
            {
                "prompt": "The line graph below shows the population growth in three different cities from 1990 to 2010. Summarize the information by selecting and reporting the main features, and make comparisons where relevant.",
                "topic": "Data Analysis",
                "task_type": "Task 1",
                "difficulty": "Easy"
            },
            {
                "prompt": "The table below shows the percentage of households with different types of technology in 2000 and 2010. Summarize the information by selecting and reporting the main features, and make comparisons where relevant.",
                "topic": "Data Analysis",
                "task_type": "Task 1",
                "difficulty": "Medium"
            },
            {
                "prompt": "Some people think that the government should provide free housing for everyone. Others believe that this is not the government's responsibility. Discuss both views and give your opinion.",
                "topic": "Government",
                "task_type": "Task 2",
                "difficulty": "Hard"
            },
            {
                "prompt": "The diagram below shows the process of how coffee is produced. Summarize the information by selecting and reporting the main features.",
                "topic": "Process",
                "task_type": "Task 1",
                "difficulty": "Easy"
            },
            {
                "prompt": "Some people believe that children should be allowed to stay at home and play until they are six or seven years old. Others believe that it is important for young children to go to school as soon as possible. Discuss both views and give your opinion.",
                "topic": "Education",
                "task_type": "Task 2",
                "difficulty": "Medium"
            },
            {
                "prompt": "The bar chart below shows the number of men and women in further education in Britain in three periods. Summarize the information by selecting and reporting the main features, and make comparisons where relevant.",
                "topic": "Education",
                "task_type": "Task 1",
                "difficulty": "Medium"
            },
            {
                "prompt": "Some people think that the best way to learn about other cultures is through traveling. Others believe that books and films are better sources of information. Discuss both views and give your opinion.",
                "topic": "Culture",
                "task_type": "Task 2",
                "difficulty": "Easy"
            },
            {
                "prompt": "The pie charts below show the percentage of water used for different purposes in six areas of the world. Summarize the information by selecting and reporting the main features, and make comparisons where relevant.",
                "topic": "Environment",
                "task_type": "Task 1",
                "difficulty": "Hard"
            },
            {
                "prompt": "Some people believe that the internet has made people more isolated. Others think that it has brought people closer together. Discuss both views and give your opinion.",
                "topic": "Technology",
                "task_type": "Task 2",
                "difficulty": "Medium"
            },
            {
                "prompt": "The map below shows the development of a small village called Chorleywood between 1868 and 1994. Summarize the information by selecting and reporting the main features.",
                "topic": "Geography",
                "task_type": "Task 1",
                "difficulty": "Hard"
            },
            {
                "prompt": "Some people think that the government should spend money on looking for life on other planets, while others believe that there are more important issues on Earth. Discuss both views and give your opinion.",
                "topic": "Science",
                "task_type": "Task 2",
                "difficulty": "Hard"
            },
            {
                "prompt": "The graph below shows the number of visitors to a museum between June and September. Summarize the information by selecting and reporting the main features.",
                "topic": "Tourism",
                "task_type": "Task 1",
                "difficulty": "Easy"
            },
            {
                "prompt": "Some people believe that advertising has a negative effect on society. Others think that advertising is beneficial. Discuss both views and give your opinion.",
                "topic": "Media",
                "task_type": "Task 2",
                "difficulty": "Medium"
            },
            {
                "prompt": "The diagram below shows the life cycle of a salmon. Summarize the information by selecting and reporting the main features.",
                "topic": "Nature",
                "task_type": "Task 1",
                "difficulty": "Medium"
            }
        ]
        
        # Create writing tests from real prompts
        for i, prompt_data in enumerate(real_prompts):
            writing_tests.append({
                "id": f"writing_real_{i+1}",
                "title": f"IELTS Writing {prompt_data['task_type']} - {prompt_data['topic']}",
                "book": None,
                "task_type": prompt_data["task_type"],
                "type": "Academic",
                "difficulty": prompt_data["difficulty"],
                "estimated_time": "20 minutes" if prompt_data["task_type"] == "Task 1" else "40 minutes",
                "word_count": 150 if prompt_data["task_type"] == "Task 1" else 250,
                "description": f"Practice {prompt_data['task_type']} on {prompt_data['topic'].lower()}",
                "prompt": prompt_data["prompt"],
                "sample_answer": None
            })
        
        # Add Cambridge IELTS writing samples
        academic_path = self.cambridge_path / "Academic"
        for test_book in academic_path.iterdir():
            if test_book.is_dir() and "Cambridge IELTS" in test_book.name:
                book_name = test_book.name
                book_number = self._extract_book_number(book_name)
                
                # Add Task 1 and Task 2 tests
                for task_type in ["Task 1", "Task 2"]:
                    writing_tests.append({
                        "id": f"writing_cambridge_{book_number}_{task_type.lower().replace(' ', '_')}",
                        "title": f"Cambridge IELTS {book_number} - {task_type}",
                        "book": book_number,
                        "task_type": task_type,
                        "type": "Academic",
                        "difficulty": self._get_difficulty_by_book(book_number),
                        "estimated_time": "20 minutes" if task_type == "Task 1" else "40 minutes",
                        "word_count": 150 if task_type == "Task 1" else 250,
                        "description": f"Practice {task_type} from Cambridge IELTS {book_number}",
                        "prompt": f"Complete {task_type} practice from Cambridge IELTS {book_number}",
                        "sample_answer": None
                    })
        
        # Add General Training writing tests
        general_path = self.cambridge_path / "General"
        for pdf_file in general_path.glob("*.pdf"):
            if "writing" in pdf_file.name.lower():
                writing_tests.append({
                    "id": f"writing_gt_{pdf_file.stem}",
                    "title": f"General Training Writing - {pdf_file.stem}",
                    "task_type": "Task 1 & Task 2",
                    "type": "General Training",
                    "difficulty": "Medium",
                    "estimated_time": "60 minutes",
                    "word_count": "150-250",
                    "description": f"General Training writing practice from {pdf_file.stem}",
                    "prompt": "Complete General Training writing tasks",
                    "pdf_file": str(pdf_file)
                })
        
        return writing_tests
    
    def get_test_by_id(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific test by ID"""
        # Try listening tests
        listening_tests = self.get_listening_tests()
        for test in listening_tests:
            if test["id"] == test_id:
                return test
        
        # Try reading tests
        reading_tests = self.get_reading_tests()
        for test in reading_tests:
            if test["id"] == test_id:
                return test
        
        # Try speaking tests
        speaking_tests = self.get_speaking_tests()
        for test in speaking_tests:
            if test["id"] == test_id:
                return test
        
        # Try writing tests
        writing_tests = self.get_writing_tests()
        for test in writing_tests:
            if test["id"] == test_id:
                return test
        
        return None
    
    def _extract_book_number(self, book_name: str) -> int:
        """Extract book number from Cambridge IELTS book name"""
        import re
        match = re.search(r'IELTS (\d+)', book_name)
        return int(match.group(1)) if match else 0
    
    def _get_difficulty_by_book(self, book_number: int) -> str:
        """Determine difficulty based on Cambridge IELTS book number"""
        if book_number <= 6:
            return "Easy"
        elif book_number <= 12:
            return "Medium"
        else:
            return "Hard"
    
    def _group_speaking_questions(self, questions: List[Dict]) -> Dict[str, List[Dict]]:
        """Group speaking questions by topic"""
        topics = {}
        
        for question in questions:
            instruction = question.get("instruction", "")
            
            # Simple topic detection based on keywords
            topic = "General Topics"
            if any(word in instruction.lower() for word in ["work", "job", "career", "profession"]):
                topic = "Work & Career"
            elif any(word in instruction.lower() for word in ["study", "education", "school", "university"]):
                topic = "Education"
            elif any(word in instruction.lower() for word in ["family", "parents", "children", "relatives"]):
                topic = "Family & Relationships"
            elif any(word in instruction.lower() for word in ["travel", "trip", "vacation", "holiday"]):
                topic = "Travel & Tourism"
            elif any(word in instruction.lower() for word in ["food", "restaurant", "cooking", "meal"]):
                topic = "Food & Dining"
            elif any(word in instruction.lower() for word in ["technology", "computer", "internet", "phone"]):
                topic = "Technology"
            elif any(word in instruction.lower() for word in ["environment", "nature", "pollution", "climate"]):
                topic = "Environment"
            
            if topic not in topics:
                topics[topic] = []
            topics[topic].append(question)
        
        return topics
    
    def _get_fallback_speaking_tests(self) -> List[Dict[str, Any]]:
        """Get fallback speaking tests when JSON files fail to load"""
        return [
            {
                "id": "speaking_fallback_work",
                "title": "Speaking Practice - Work & Career",
                "type": "Speaking",
                "topic": "Work & Career",
                "difficulty": "Mixed",
                "estimated_time": "15 minutes",
                "questions": [
                    {"instruction": "Do you work or are you a student?"},
                    {"instruction": "What do you like about your job?"},
                    {"instruction": "What are your future career plans?"},
                    {"instruction": "Do you think technology will change your job?"},
                    {"instruction": "What skills are important for your job?"}
                ],
                "description": "Practice speaking about work and career with common IELTS questions",
                "total_questions": 5
            },
            {
                "id": "speaking_fallback_education",
                "title": "Speaking Practice - Education",
                "type": "Speaking",
                "topic": "Education",
                "difficulty": "Mixed",
                "estimated_time": "15 minutes",
                "questions": [
                    {"instruction": "What did you study at school?"},
                    {"instruction": "Do you think education is important?"},
                    {"instruction": "What was your favorite subject?"},
                    {"instruction": "Do you prefer online or traditional learning?"},
                    {"instruction": "What would you like to study in the future?"}
                ],
                "description": "Practice speaking about education with common IELTS questions",
                "total_questions": 5
            },
            {
                "id": "speaking_fallback_travel",
                "title": "Speaking Practice - Travel & Tourism",
                "type": "Speaking",
                "topic": "Travel & Tourism",
                "difficulty": "Mixed",
                "estimated_time": "15 minutes",
                "questions": [
                    {"instruction": "Do you like traveling?"},
                    {"instruction": "What's your favorite place to visit?"},
                    {"instruction": "Do you prefer traveling alone or with others?"},
                    {"instruction": "What do you like to do when you travel?"},
                    {"instruction": "Where would you like to travel in the future?"}
                ],
                "description": "Practice speaking about travel and tourism with common IELTS questions",
                "total_questions": 5
            }
        ]

# Global instance
test_data_service = TestDataService()
