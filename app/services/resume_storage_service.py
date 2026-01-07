import sqlite3
import json
from datetime import datetime

DB_PATH = "resumes.db"


def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS resumes (
            candidate_id TEXT PRIMARY KEY,
            resume_json TEXT,
            created_at TEXT
        )
    """
    )
    conn.commit()
    conn.close()


def store_resume(candidate_id: str, resume_data: dict):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO resumes (candidate_id, resume_json, created_at)
        VALUES (?, ?, ?)
        """,
        (candidate_id, json.dumps(resume_data), datetime.utcnow().isoformat()),
    )

    conn.commit()
    conn.close()


def get_resume(candidate_id: str) -> dict | None:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT resume_json FROM resumes WHERE candidate_id = ?", (candidate_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return json.loads(row[0])
