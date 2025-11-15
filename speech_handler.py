import os
import base64
from openai import OpenAI
from typing import Tuple
import tempfile


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))


async def transcribe_audio(audio_base64: str) -> Tuple[str, float]:
    """
    Transcribe audio using OpenAI Whisper API.

    Args:
        audio_base64: Base64 encoded audio data

    Returns:
        Tuple of (transcribed_text, confidence_score)

    Raises:
        Exception: If transcription fails
    """
    try:
        # Decode base64 audio
        audio_data = base64.b64decode(audio_base64)

        # Create temporary file to save audio (Whisper API requires file input)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_data)
            temp_audio_path = temp_audio.name

        try:
            # Call Whisper API
            with open(temp_audio_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json"
                )

            # Extract text and confidence (if available)
            transcribed_text = transcript.text

            # Whisper doesn't provide confidence scores in the standard response
            # We'll use a placeholder or estimate based on response
            confidence_score = 0.85  # Default confidence

            return transcribed_text, confidence_score

        finally:
            # Clean up temporary file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)

    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")


# Fallback for testing without API calls
def mock_transcribe_audio(audio_base64: str) -> Tuple[str, float]:
    """
    Mock transcription for testing without burning API credits.
    Returns hardcoded responses based on input length.
    """
    # Simple mock based on input length
    length = len(audio_base64)

    mock_responses = [
        "I completed the user dashboard this week and started working on the API integration.",
        "The project is delayed by two days because the documentation for the third-party API is incomplete.",
        "I need help with the performance optimization. I've been stuck on it for three days.",
        "Everything is on track. I finished the login feature and it's ready for review.",
        "I'm waiting for the design team to send the final mockups before I can proceed."
    ]

    # Use length to select a mock response
    index = (length % len(mock_responses))
    return mock_responses[index], 0.9
