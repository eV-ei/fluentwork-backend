import os
from openai import OpenAI
from models import Session, Feedback, MessageRole
import re


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_conversation(session: Session) -> Feedback:
    """
    Analyze user's performance in the conversation and generate feedback.

    Evaluates:
    - Clarity: Did they communicate the main point?
    - Fluency: Hesitations, filler words, natural flow
    - Professional language: Workplace appropriate phrases

    Returns only ONE improvement tip to keep feedback actionable.
    """
    try:
        # Extract user messages
        user_messages = [
            msg.content for msg in session.conversation_history
            if msg.role == MessageRole.USER
        ]

        if not user_messages:
            return _generate_default_feedback()

        # Build analysis prompt
        conversation_text = "\n".join([f"User: {msg}" for msg in user_messages])
        scenario_context = f"Scenario: {session.scenario.primary_topic}\nContext: {session.scenario.context}"

        analysis_prompt = f"""Analyze this workplace 1:1 conversation for a non-native English speaker practicing professional communication.

{scenario_context}

Conversation:
{conversation_text}

Evaluate on three dimensions (score 0-10):

1. CLARITY (0-10): Did they clearly communicate their main point? Were they specific or vague?
2. FLUENCY (0-10): Natural flow, minimal filler words, coherent sentences
3. PROFESSIONAL (0-10): Workplace-appropriate language, professional tone

Provide scores and identify THE MOST IMPORTANT improvement area. Return ONLY ONE specific, actionable tip.

Format your response as:
CLARITY: [score]
FLUENCY: [score]
PROFESSIONAL: [score]
ONE_IMPROVEMENT: [one specific actionable tip in 1-2 sentences]"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert English communication coach for workplace scenarios."},
                {"role": "user", "content": analysis_prompt}
            ],
            max_tokens=300,
            temperature=0.3
        )

        analysis_text = response.choices[0].message.content.strip()

        # Parse the response
        clarity_score = _extract_score(analysis_text, "CLARITY")
        fluency_score = _extract_score(analysis_text, "FLUENCY")
        professional_score = _extract_score(analysis_text, "PROFESSIONAL")
        improvement_tip = _extract_improvement(analysis_text)

        return Feedback(
            clarity_score=clarity_score,
            fluency_score=fluency_score,
            professional_score=professional_score,
            improvement_tip=improvement_tip,
            detailed_analysis=analysis_text
        )

    except Exception as e:
        # Return fallback feedback on error
        return _generate_default_feedback()


def _extract_score(text: str, category: str) -> float:
    """Extract score from analysis text."""
    pattern = rf"{category}:\s*(\d+(?:\.\d+)?)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        score = float(match.group(1))
        return min(max(score, 0), 10)  # Clamp between 0-10
    return 7.0  # Default score


def _extract_improvement(text: str) -> str:
    """Extract improvement tip from analysis text."""
    pattern = r"ONE_IMPROVEMENT:\s*(.+?)(?:\n\n|\Z)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return "Practice being more specific when describing your work and challenges."


def _generate_default_feedback() -> Feedback:
    """Generate default feedback when analysis fails."""
    return Feedback(
        clarity_score=7.0,
        fluency_score=7.0,
        professional_score=7.0,
        improvement_tip="Great practice session! Focus on being more specific when describing your work and any blockers you encounter."
    )


# Simple rule-based analysis for common patterns
def _analyze_fluency_patterns(text: str) -> dict:
    """
    Analyze text for fluency indicators.
    Returns dict with findings.
    """
    filler_words = ["um", "uh", "like", "you know", "actually", "basically", "just"]
    repetitions = []

    findings = {
        "filler_count": 0,
        "avg_sentence_length": 0,
        "has_repetition": False
    }

    text_lower = text.lower()

    # Count filler words
    for filler in filler_words:
        findings["filler_count"] += text_lower.count(f" {filler} ")

    # Check sentence length
    sentences = text.split(".")
    if sentences:
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
        findings["avg_sentence_length"] = avg_length

    return findings


# Mock function for testing without API calls
def mock_analyze_conversation(session: Session) -> Feedback:
    """
    Generate mock feedback for testing without API calls.
    """
    user_messages = [
        msg.content for msg in session.conversation_history
        if msg.role == MessageRole.USER
    ]

    if not user_messages:
        return _generate_default_feedback()

    # Simple analysis based on message characteristics
    total_words = sum(len(msg.split()) for msg in user_messages)
    avg_words = total_words / len(user_messages) if user_messages else 0

    # Score based on average message length (proxy for detail)
    clarity_score = min(10, max(5, avg_words / 2))

    # Mock fluency based on message count
    fluency_score = min(10, 6 + len(user_messages) * 0.5)

    # Mock professional score
    professional_score = 8.0

    # Generate improvement based on lowest score
    if clarity_score < fluency_score and clarity_score < professional_score:
        tip = "Try to be more specific and provide more details when explaining your work or challenges."
    elif fluency_score < professional_score:
        tip = "Practice speaking more naturally. Take your time and use complete sentences."
    else:
        tip = "Great job! Consider using more professional phrases like 'I'm working on' instead of 'I'm doing'."

    return Feedback(
        clarity_score=round(clarity_score, 1),
        fluency_score=round(fluency_score, 1),
        professional_score=round(professional_score, 1),
        improvement_tip=tip
    )
