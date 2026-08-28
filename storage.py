"""
Storage & Reporting Module (M6)

Responsibility:
    Persist enumerated URLs, metadata, and liveness status; generate
    summary reports/dashboards of discovered active services.

Status: SCAFFOLD — interfaces only, implementation pending (Week 10-12).
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ServiceRecord:
    url: str
    first_seen_at: str
    last_checked_at: str
    is_active: bool
    is_mirror_of: Optional[str] = None
    source: Optional[str] = None


class DataStore:
    """Interface over the chosen backing store (PostgreSQL / MongoDB)."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def upsert(self, record: ServiceRecord) -> None:
        """Insert or update a service record.

        TODO: implement DB write with the chosen driver/ORM.
        """
        raise NotImplementedError

    def query_active(self) -> List[ServiceRecord]:
        """Return all currently-active, non-mirror service records.

        TODO: implement query.
        """
        raise NotImplementedError

    def generate_summary_report(self) -> dict:
        """Produce summary statistics: total enumerated, active count,
        mirror-rate, coverage per seed source, etc.

        TODO: implement aggregation queries and report formatting.
        """
        raise NotImplementedError
