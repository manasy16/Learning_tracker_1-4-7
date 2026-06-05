# SQLite logic
import sqlite3
from datetime import datetime, timedelta

from paths import DB_PATH, ensure_data_dirs

ensure_data_dirs()


def get_connection():
    return sqlite3.connect(str(DB_PATH), timeout=10)


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                topic       TEXT NOT NULL,
                date_logged TEXT NOT NULL,
                rev1_date   TEXT NOT NULL,
                rev2_date   TEXT NOT NULL,
                rev3_date   TEXT NOT NULL,
                rev1_done   INTEGER DEFAULT 0,
                rev2_done   INTEGER DEFAULT 0,
                rev3_done   INTEGER DEFAULT 0
            )
        """)
        conn.commit()


def add_topic(topic: str):
    today = datetime.now().date()
    rev1 = (today + timedelta(days=1)).isoformat()
    rev2 = (today + timedelta(days=4)).isoformat()
    rev3 = (today + timedelta(days=7)).isoformat()
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO topics
               (topic, date_logged, rev1_date, rev2_date, rev3_date)
               VALUES (?, ?, ?, ?, ?)""",
            (topic.strip(), today.isoformat(), rev1, rev2, rev3)
        )
        conn.commit()


def get_due_today():
    today = datetime.now().date().isoformat()
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT id, topic,
                CASE
                    WHEN rev1_date <= ? AND rev1_done = 0 THEN 1
                    WHEN rev2_date <= ? AND rev2_done = 0 THEN 2
                    WHEN rev3_date <= ? AND rev3_done = 0 THEN 3
                END as rev_num
            FROM topics
            WHERE (rev1_date <= ? AND rev1_done = 0)
               OR (rev2_date <= ? AND rev2_done = 0)
               OR (rev3_date <= ? AND rev3_done = 0)
            ORDER BY date_logged ASC, id ASC
        """, (today, today, today, today, today, today))
        return [
            {"id": row[0], "topic": row[1], "rev_num": row[2]}
            for row in cursor.fetchall()
        ]


def mark_revised(topic_id: int, rev_num: int):
    columns = {
        1: "rev1_done",
        2: "rev2_done",
        3: "rev3_done",
    }
    col = columns.get(int(rev_num))
    if not col:
        raise ValueError(f"Invalid revision number: {rev_num}")

    with get_connection() as conn:
        conn.execute(f"UPDATE topics SET {col} = 1 WHERE id = ?", (int(topic_id),))
        conn.commit()


def get_topics_logged_today():
    today = datetime.now().date().isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM topics WHERE date_logged = ?", (today,)
        )
        return cursor.fetchone()[0]
