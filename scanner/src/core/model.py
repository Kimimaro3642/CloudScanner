from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Finding:
    id: str
    service: str
    resource: str
    rule: str
    description: str
    severity: str
    mitre: str
    cvss_score: float = 0.0
    references: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
