from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.core.security import get_current_user
from app.services.test_data_service import test_data_service

router = APIRouter(prefix="/api/v1/test-library", tags=["test-library"])

class TestResponse(BaseModel):
    id: str
    title: str
    type: str
    difficulty: str
    estimated_time: str
    description: str

class ListeningTestResponse(TestResponse):
    book: int
    test_number: str
    sections: List[Dict[str, Any]]
    total_sections: int

class ReadingTestResponse(TestResponse):
    book: int
    pdf_file: str
    total_passages: int
    total_questions: int

class SpeakingTestResponse(TestResponse):
    topic: str
    questions: List[Dict[str, Any]]
    total_questions: int

class WritingTestResponse(TestResponse):
    book: Optional[int] = None
    task_type: str
    word_count: Any
    prompt: str
    sample_answer: Optional[str] = None
    pdf_file: Optional[str] = None

@router.get("/listening", response_model=List[ListeningTestResponse])
async def get_listening_tests(current_user: dict = Depends(get_current_user)):
    """Get all available listening tests"""
    try:
        tests = test_data_service.get_listening_tests()
        return tests
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading listening tests: {str(e)}"
        )

@router.get("/reading", response_model=List[ReadingTestResponse])
async def get_reading_tests(current_user: dict = Depends(get_current_user)):
    """Get all available reading tests"""
    try:
        tests = test_data_service.get_reading_tests()
        return tests
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading reading tests: {str(e)}"
        )

@router.get("/speaking", response_model=List[SpeakingTestResponse])
async def get_speaking_tests(current_user: dict = Depends(get_current_user)):
    """Get all available speaking tests"""
    try:
        tests = test_data_service.get_speaking_tests()
        return tests
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading speaking tests: {str(e)}"
        )

@router.get("/writing", response_model=List[WritingTestResponse])
async def get_writing_tests(current_user: dict = Depends(get_current_user)):
    """Get all available writing tests"""
    try:
        tests = test_data_service.get_writing_tests()
        return tests
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading writing tests: {str(e)}"
        )

@router.get("/test/{test_id}")
async def get_test_by_id(test_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific test by ID"""
    try:
        test = test_data_service.get_test_by_id(test_id)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found"
            )
        return test
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading test: {str(e)}"
        )

@router.get("/stats")
async def get_test_library_stats(current_user: dict = Depends(get_current_user)):
    """Get statistics about available tests"""
    try:
        listening_tests = test_data_service.get_listening_tests()
        reading_tests = test_data_service.get_reading_tests()
        speaking_tests = test_data_service.get_speaking_tests()
        writing_tests = test_data_service.get_writing_tests()
        
        return {
            "total_tests": len(listening_tests) + len(reading_tests) + len(speaking_tests) + len(writing_tests),
            "listening_tests": len(listening_tests),
            "reading_tests": len(reading_tests),
            "speaking_tests": len(speaking_tests),
            "writing_tests": len(writing_tests),
            "difficulty_breakdown": {
                "easy": sum(1 for test in listening_tests + reading_tests + speaking_tests + writing_tests if test.get("difficulty") == "Easy"),
                "medium": sum(1 for test in listening_tests + reading_tests + speaking_tests + writing_tests if test.get("difficulty") == "Medium"),
                "hard": sum(1 for test in listening_tests + reading_tests + speaking_tests + writing_tests if test.get("difficulty") == "Hard")
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading test statistics: {str(e)}"
        )


