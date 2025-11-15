import os
from openai import OpenAI
from models import Session, Message, MessageRole, Scenario
from typing import Tuple
from datetime import datetime, timedelta


# Initialize OpenAI client (will use OPENAI_API_KEY env var)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

SYSTEM_PROMPT = """You are a professional, neutral manager in a 1:1 meeting with your team member.

Guidelines:
- Keep responses brief (1-2 sentences maximum)
- Ask natural follow-up questions based on what the user shares
- Be supportive but professional
- If the user mentions delays or blockers, ask about impact or solutions
- If the user is vague, ask for clarification
- Don't be overly enthusiastic or dramatic
- Use casual professional language (like real workplace conversations)

Remember: You're helping an employee practice workplace communication, so respond as a real manager would."""


def get_manager_response(
    session: Session,
    user_message: str
) -> Tuple[str, bool]:
    """
    Generate manager response using GPT-4.

    Args:
        session: Current conversation session
        user_message: User's latest message

    Returns:
        Tuple of (manager_response, should_end_session)
    """
    try:
        # Build conversation history
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add scenario context
        scenario_context = f"""Current scenario: {session.scenario.primary_topic}
Context: {session.scenario.context}
Your first question was: {session.scenario.initial_prompt}"""

        messages.append({"role": "system", "content": scenario_context})

        # Add conversation history
        for msg in session.conversation_history:
            role = "assistant" if msg.role == MessageRole.MANAGER else "user"
            messages.append({"role": role, "content": msg.content})

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Determine if we should introduce surprise element
        exchange_count = len(session.conversation_history) // 2
        if (session.scenario.surprise_element and
            exchange_count >= 2 and
            exchange_count <= 4 and
            not _surprise_already_introduced(session)):
            # Add surprise element instruction
            surprise_instruction = f"\n\nNow introduce this element naturally: {session.scenario.surprise_element}"
            messages[-1]["content"] += surprise_instruction

        # Check if we should end the conversation
        should_end = _should_end_conversation(session)

        if should_end:
            # Add ending instruction
            messages.append({
                "role": "system",
                "content": "Wrap up the conversation naturally in 1 sentence. Thank them or say something like 'Thanks for the update' or 'Keep me posted'"
            })

        # Call GPT-4
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=100,
            temperature=0.7
        )

        manager_response = response.choices[0].message.content.strip()

        return manager_response, should_end

    except Exception as e:
        # Fallback response on error
        return "I see. Can you tell me more about that?", False


def _should_end_conversation(session: Session) -> bool:
    """
    Determine if conversation should end based on:
    - Number of exchanges (6-8 exchanges)
    - Time duration (4-5 minutes)
    """
    exchange_count = len(session.conversation_history) // 2

    # End after 6-8 exchanges
    if exchange_count >= 6:
        return True

    # End after 5 minutes
    max_duration = int(os.getenv("MAX_SESSION_DURATION", "300"))
    elapsed = (datetime.now() - session.start_time).total_seconds()
    if elapsed >= max_duration:
        return True

    return False


def _surprise_already_introduced(session: Session) -> bool:
    """Check if surprise element keywords appear in conversation history."""
    if not session.scenario.surprise_element:
        return False

    # Simple check: see if any keywords from surprise element appear in manager responses
    surprise_keywords = session.scenario.surprise_element.lower().split()[:3]

    for msg in session.conversation_history:
        if msg.role == MessageRole.MANAGER:
            msg_lower = msg.content.lower()
            if any(keyword in msg_lower for keyword in surprise_keywords):
                return True

    return False


# Mock function for testing without API calls
def mock_get_manager_response(
    session: Session,
    user_message: str
) -> Tuple[str, bool]:
    """
    Mock manager responses for testing without burning API credits.
    """
    exchange_count = len(session.conversation_history) // 2

    # Predefined responses based on exchange count
    responses = [
        "That sounds good. How's the timeline looking?",
        "I see. Is there anything blocking you?",
        "Understood. What's your plan to move forward?",
        "Makes sense. Do you need any support from me?",
        "Got it. Keep me posted on how it goes.",
        "Thanks for the update. Let me know if anything comes up."
    ]

    # Select response based on exchange count
    response_index = min(exchange_count, len(responses) - 1)
    manager_response = responses[response_index]

    # Introduce surprise element at exchange 3
    if (session.scenario.surprise_element and
        exchange_count == 2 and
        not _surprise_already_introduced(session)):
        manager_response = f"Hmm, {session.scenario.surprise_element.lower()}. How does that affect things?"

    # End after 6 exchanges
    should_end = exchange_count >= 5

    return manager_response, should_end
