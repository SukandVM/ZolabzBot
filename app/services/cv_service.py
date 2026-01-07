def analyze_frame(frame_path: str) -> dict:
    """
    CV Core Contract (FROZEN)

    Input:
        frame_path (str): image/frame path

    Output:
        {
            "violation": bool,
            "violation_type": str | None,
            "confidence": float | None
        }
    """

    # TEMPORARY MOCK
    return {"violation": False, "violation_type": None, "confidence": 0.0}
