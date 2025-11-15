from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uuid
from datetime import datetime
from collections import OrderedDict

from models import (
    Session, Message, MessageRole, UserProgress,
    StartSessionResponse, SpeechToTextRequest, SpeechToTextResponse,
    GetManagerResponseRequest, GetManagerResponseResponse,
    GetFeedbackResponse, UserProgressResponse
)
from scenarios import select_scenario_for_user, determine_next_complexity
from conversation_engine import get_manager_response, mock_get_manager_response
from speech_handler import transcribe_audio, mock_transcribe_audio
from feedback_analyzer import analyze_conversation, mock_analyze_conversation


# Load environment variables
load_dotenv()

app = FastAPI(title="FluentWork API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (no database for MVP)
sessions: OrderedDict[str, Session] = OrderedDict()
user_progress = UserProgress()

# Configuration
MAX_SESSIONS_IN_MEMORY = 100
USE_MOCK_MODE = False  # Set to True to test without OpenAI API calls


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "FluentWork API is running",
        "version": "1.0.0",
        "endpoints": [
            "/start-session",
            "/speech-to-text",
            "/get-manager-response",
            "/get-feedback",
            "/user-progress"
        ]
    }


@app.post("/start-session", response_model=StartSessionResponse)
async def start_session():
    """
    Start a new practice session.

    Returns:
        session_id: Unique identifier for the session
        scenario_description: Description of the scenario
        initial_prompt: Manager's opening question
        helpful_phrases: 3-4 useful phrases for this scenario
    """
    try:
        # Select appropriate scenario based on user progress
        scenario = select_scenario_for_user(user_progress)

        # Create new session
        session_id = str(uuid.uuid4())
        session = Session(
            id=session_id,
            scenario=scenario,
            conversation_history=[],
            start_time=datetime.now(),
            is_active=True
        )

        # Add initial manager message to history
        initial_message = Message(
            role=MessageRole.MANAGER,
            content=scenario.initial_prompt,
            timestamp=datetime.now()
        )
        session.conversation_history.append(initial_message)

        # Store session (keep only last 100 sessions)
        sessions[session_id] = session
        if len(sessions) > MAX_SESSIONS_IN_MEMORY:
            sessions.popitem(last=False)  # Remove oldest session

        return StartSessionResponse(
            session_id=session_id,
            scenario_description=scenario.context,
            initial_prompt=scenario.initial_prompt,
            helpful_phrases=scenario.helpful_phrases
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")


@app.post("/speech-to-text", response_model=SpeechToTextResponse)
async def speech_to_text(request: SpeechToTextRequest):
    """
    Convert speech audio to text using Whisper API.

    Args:
        request: Contains base64 encoded audio

    Returns:
        Transcribed text and confidence score
    """
    try:
        if USE_MOCK_MODE:
            transcribed_text, confidence = mock_transcribe_audio(request.audio_base64)
        else:
            transcribed_text, confidence = await transcribe_audio(request.audio_base64)

        return SpeechToTextResponse(
            transcribed_text=transcribed_text,
            confidence_score=confidence
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@app.post("/get-manager-response", response_model=GetManagerResponseResponse)
async def get_manager_response_endpoint(request: GetManagerResponseRequest):
    """
    Get AI manager's response to user's message.

    Args:
        request: Contains session_id and user_message

    Returns:
        Manager's response and whether session should end
    """
    try:
        # Validate session exists
        session = sessions.get(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if not session.is_active:
            raise HTTPException(status_code=400, detail="Session is no longer active")

        # Add user message to history
        user_message = Message(
            role=MessageRole.USER,
            content=request.user_message,
            timestamp=datetime.now()
        )
        session.conversation_history.append(user_message)

        # Get manager response
        if USE_MOCK_MODE:
            manager_response, should_end = mock_get_manager_response(session, request.user_message)
        else:
            manager_response, should_end = get_manager_response(session, request.user_message)

        # Add manager response to history
        manager_message = Message(
            role=MessageRole.MANAGER,
            content=manager_response,
            timestamp=datetime.now()
        )
        session.conversation_history.append(manager_message)

        # Mark session as inactive if it should end
        if should_end:
            session.is_active = False

        return GetManagerResponseResponse(
            manager_response=manager_response,
            should_end_session=should_end
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get response: {str(e)}")


@app.post("/get-feedback", response_model=GetFeedbackResponse)
async def get_feedback(session_id: str):
    """
    Get feedback analysis for a completed session.

    Args:
        session_id: Session identifier

    Returns:
        Performance scores and one actionable improvement tip
    """
    try:
        # Validate session exists
        session = sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Analyze conversation
        if USE_MOCK_MODE:
            feedback = mock_analyze_conversation(session)
        else:
            feedback = analyze_conversation(session)

        # Update user progress
        user_progress.total_sessions += 1
        user_progress.last_session_date = datetime.now()
        user_progress.current_complexity = determine_next_complexity(user_progress)

        # Simple streak calculation (would need date tracking for real implementation)
        if user_progress.total_sessions > 0:
            user_progress.streak_days = 1  # Simplified for MVP

        return GetFeedbackResponse(
            clarity_score=feedback.clarity_score,
            fluency_score=feedback.fluency_score,
            professional_score=feedback.professional_score,
            one_improvement=feedback.improvement_tip
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate feedback: {str(e)}")


@app.get("/user-progress", response_model=UserProgressResponse)
async def get_user_progress():
    """
    Get user's overall progress and stats.

    Returns:
        Total sessions completed, current level, and streak
    """
    return UserProgressResponse(
        sessions_completed=user_progress.total_sessions,
        current_level=user_progress.current_complexity.value,
        streak=user_progress.streak_days
    )


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session (cleanup endpoint).

    Args:
        session_id: Session to delete
    """
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "Session deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@app.post("/reset-progress")
async def reset_progress():
    """
    Reset user progress (for testing/development).
    """
    global user_progress
    user_progress = UserProgress()
    sessions.clear()
    return {"message": "Progress reset successfully"}


# For development/testing
@app.get("/debug/sessions")
async def debug_sessions():
    """Debug endpoint to view all active sessions."""
    return {
        "total_sessions": len(sessions),
        "sessions": [
            {
                "id": s.id,
                "scenario": s.scenario.primary_topic,
                "exchanges": len(s.conversation_history) // 2,
                "is_active": s.is_active
            }
            for s in sessions.values()
        ]
    }


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
