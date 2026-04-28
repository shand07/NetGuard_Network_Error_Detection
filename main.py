
from models.check_result import CheckResult
from repositories.db import get_conn


class CheckResultRepository:

    def add(self, result: CheckResult) -> CheckResult:
        with get_conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO check_results
                (endpoint_id, ts, latency_ms, status, http_status, error_type, error_message, llm_label, llm_analysis)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.endpoint_id,
                    result.ts,
                    result.latency_ms,
                    result.status,
                    result.http_status,
                    result.error_type,
                    result.error_message,
                    result.llm_label,
                    result.llm_analysis,
                )
            )
            result.id = cur.lastrowid
            conn.commit()
        return result

    def list_all(self):
        with get_conn() as conn:
            rows = conn.execute(
                """
                SELECT id, endpoint_id, ts, latency_ms, status, http_status, error_type, error_message, llm_label, llm_analysis
                FROM check_results
                ORDER BY id DESC
                """
            ).fetchall()

        return [
            CheckResult(
                id=row[0],
                endpoint_id=row[1],
                ts=row[2],
                latency_ms=row[3],
                status=row[4],
                http_status=row[5],
                error_type=row[6],
                error_message=row[7],
                llm_label=row[8],
                llm_analysis=row[9],
            )
            for row in rows
        ]

    def clear_all(self):
        with get_conn() as conn:
            conn.execute("DELETE FROM check_results")
            conn.commit()
