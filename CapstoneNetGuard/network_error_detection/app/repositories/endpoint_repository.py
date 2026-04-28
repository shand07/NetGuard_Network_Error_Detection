
from models.endpoint import Endpoint
from repositories.db import get_conn


class EndpointRepository:

    def add(self, endpoint: Endpoint) -> Endpoint:
        with get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO endpoints (name, url, enabled, expected_latency_ms) VALUES (?, ?, ?, ?)",
                (endpoint.name, endpoint.url, 1 if endpoint.enabled else 0, endpoint.expected_latency_ms)
            )
            endpoint.id = cur.lastrowid
            conn.commit()

        return endpoint

    def list_all(self):
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT id, name, url, enabled, expected_latency_ms FROM endpoints"
            ).fetchall()

        return [
            Endpoint(
                id=row[0],
                name=row[1],
                url=row[2],
                enabled=bool(row[3]),
                expected_latency_ms=row[4]
            )
            for row in rows
        ]

    def delete(self, endpoint_id: int):
        with get_conn() as conn:
            conn.execute("DELETE FROM check_results WHERE endpoint_id = ?", (endpoint_id,))
            conn.execute("DELETE FROM endpoints WHERE id = ?", (endpoint_id,))
            conn.commit()

    def clear_all(self):
        with get_conn() as conn:
            conn.execute("DELETE FROM check_results")
            conn.execute("DELETE FROM endpoints")
            conn.commit()
