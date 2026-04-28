
from dataclasses import dataclass

@dataclass
class Endpoint:
    id: int | None
    name: str
    url: str
    enabled: bool = True
    expected_latency_ms: int = 500
