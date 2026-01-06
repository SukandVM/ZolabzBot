def generate_interview_report(candidate_id: str, session: dict) -> dict:
    results = session.get("results", [])

    total_questions = len(results)

    average_score = (
        sum(r["score"] for r in results) / total_questions if total_questions > 0 else 0
    )

    return {
        "candidate_id": candidate_id,
        "status": session["status"],
        "total_questions": total_questions,
        "average_score": round(average_score, 2),
        "results": results,
    }
