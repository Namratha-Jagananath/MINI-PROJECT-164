"""
Seed Acquisition Module (M1)

Responsibility:
    Collect candidate .onion addresses from multiple independent sources
    (onion search engines, surface-web forums, threat-intel feeds),
    normalize them, and queue them for the crawler module.

Status: SCAFFOLD — interfaces only, implementation pending (Week 4-6).
"""

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class Seed:
    url: str
    source: str
    discovered_at: str


class SeedSource:
    """Base interface for a single seed source (e.g. one search engine or feed)."""

    name: str = "unnamed-source"

    def fetch_candidates(self) -> Iterable[Seed]:
        """Return an iterable of candidate Seed objects from this source.

        TODO: implement per-source fetch logic. Each concrete source should
        respect that source's terms of use / API rate limits.
        """
        raise NotImplementedError


class SeedAcquisitionManager:
    """Aggregates candidates from all configured SeedSource instances."""

    def __init__(self, sources: List[SeedSource]):
        self.sources = sources

    def collect(self) -> List[Seed]:
        """Run all sources and return a deduplicated list of raw candidate seeds.

        TODO: normalize URLs (strip tracking params, canonical form),
        deduplicate by URL, and hand off to the crawler queue.
        """
        raise NotImplementedError
