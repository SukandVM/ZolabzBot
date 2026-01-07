def transcribe_audio(audio_path: str) -> dict:
    """
    ASR Core Contract (FROZEN)

    Input:
        audio_path (str): path to audio file (wav/mp3)

    Output:
        {
            "transcript": str,
            "confidence": float | None
        }
    """

    # TEMPORARY MOCK (for backend testing)
    return {
        "transcript": "This is a mocked ASR transcription for testing.",
        "confidence": 0.9,
    }
