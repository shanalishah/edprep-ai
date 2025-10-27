from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from ..core.security import get_current_user
from ..services.ai_speaking_bot import ai_speaking_bot

router = APIRouter()
logger = logging.getLogger(__name__)

class StartBotTestRequest(BaseModel):
    test_id: str
    user_profile: Optional[Dict[str, Any]] = None

class BotResponseRequest(BaseModel):
    session_id: str
    user_response: str

class CompleteBotTestRequest(BaseModel):
    session_id: str

@router.post("/start-bot-test")
async def start_bot_test(
    request: StartBotTestRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Start an AI-powered IELTS speaking test with voice-to-voice conversation.
    """
    try:
        logger.info(f"Starting AI speaking bot test for user: {current_user.get('id', 'guest')}")
        
        session_data = await ai_speaking_bot.start_test_session(
            test_id=request.test_id,
            user_profile=request.user_profile
        )
        
        return JSONResponse(content={
            "success": True,
            "message": "AI speaking test session started successfully",
            "session_data": session_data
        })
        
    except Exception as e:
        logger.error(f"Error starting bot test: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Failed to start AI speaking test",
                "details": str(e)
            }
        )

@router.post("/process-response")
async def process_bot_response(
    request: BotResponseRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Process user's spoken response and get bot's next question/feedback.
    """
    try:
        logger.info(f"Processing bot response for session: {request.session_id}")
        
        response_data = await ai_speaking_bot.process_user_response(
            user_audio_text=request.user_response,
            session_id=request.session_id
        )
        
        return JSONResponse(content={
            "success": True,
            "message": "Response processed successfully",
            "response_data": response_data
        })
        
    except Exception as e:
        logger.error(f"Error processing bot response: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Failed to process response",
                "details": str(e)
            }
        )

@router.post("/complete-bot-test")
async def complete_bot_test(
    request: CompleteBotTestRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Complete the AI speaking test and get comprehensive assessment.
    """
    try:
        logger.info(f"Completing bot test for session: {request.session_id}")
        
        results = await ai_speaking_bot.complete_test(
            session_id=request.session_id
        )
        
        return JSONResponse(content={
            "success": True,
            "message": "AI speaking test completed successfully",
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Error completing bot test: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Failed to complete test",
                "details": str(e)
            }
        )

@router.get("/bot-health")
async def bot_health_check():
    """
    Check if the AI speaking bot service is healthy.
    """
    try:
        return JSONResponse(content={
            "status": "healthy",
            "service": "ai_speaking_bot",
            "timestamp": datetime.now().isoformat(),
            "features": [
                "voice_to_voice_conversation",
                "real_time_assessment",
                "ielts_examiner_personality",
                "comprehensive_feedback"
            ]
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


