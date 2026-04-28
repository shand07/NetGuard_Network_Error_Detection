from dataclasses import dataclass

@dataclass
class CheckResult:
    id: int | None
    endpoint_id: int
    ts: str
    latency_ms: int | None
    status: str
    http_status: int | None
    error_type: str | None
    error_message: str | None
    llm_label: str | None = None
    llm_analysis: str | None = None
