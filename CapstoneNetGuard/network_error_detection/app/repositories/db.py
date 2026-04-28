import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "database" / "app.db"

def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def column_exists(conn, table_name, column_name):
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(row[1] == column_name for row in rows)

def migrate() -> None:
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS endpoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1,
            expected_latency_ms INTEGER NOT NULL DEFAULT 500
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS check_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint_id INTEGER NOT NULL,
            ts TEXT NOT NULL,
            latency_ms INTEGER,
            status TEXT NOT NULL,
            http_status INTEGER,
            error_type TEXT,
            error_message TEXT,
            FOREIGN KEY(endpoint_id) REFERENCES endpoints(id)
        )
        """)

        if not column_exists(conn, "check_results", "llm_label"):
            conn.execute("ALTER TABLE check_results ADD COLUMN llm_label TEXT")

        if not column_exists(conn, "check_results", "llm_analysis TEXT"):
            try:
                conn.execute("ALTER TABLE check_results ADD COLUMN llm_analysis TEXT")
            except:
                pass

        conn.commit()
