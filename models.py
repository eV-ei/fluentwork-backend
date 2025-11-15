from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class ComplexityLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class MessageRole(str, Enum):
    MANAGER = "manager"
    USER = "user"


class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = datetime.now()


class Scenario(BaseModel):
    id: str
    primary_topic: str
    complexity_level: ComplexityLevel
    surprise_element: Optional[str] = None
    context: str
    initial_prompt: str
    helpful_phrases: List[str] = []


class Session(BaseModel):
    id: str
    scenario: Scenario
    conversation_history: List[Message] = []
    start_time: datetime = datetime.now()
    is_active: bool = True


class Feedback(BaseModel):
    clarity_score: float  # 0-10
    fluency_score: float  # 0-10
    professional_score: float  # 0-10
    improvement_tip: str
    detailed_analysis: Optional[str] = None


class UserProgress(BaseModel):
    total_sessions: int = 0
    current_complexity: ComplexityLevel = ComplexityLevel.EASY
    streak_days: int = 0
    last_session_date: Optional[datetime] = None


# Request/Response Models for API
class StartSessionResponse(BaseModel):
    session_id: str
    scenario_description: str
    initial_prompt: str
    helpful_phrases: List[str] = []


class SpeechToTextRequest(BaseModel):
    audio_base64: str


class SpeechToTextResponse(BaseModel):
    transcribed_text: str
    confidence_score: Optional[float] = None


class GetManagerResponseRequest(BaseModel):
    session_id: str
    user_message: str


class GetManagerResponseResponse(BaseModel):
    manager_response: str
    should_end_session: bool


class GetFeedbackResponse(BaseModel):
    clarity_score: float
    fluency_score: float
    professional_score: float
    one_improvement: str


class UserProgressResponse(BaseModel):
    sessions_completed: int
    current_level: str
    streak: int
