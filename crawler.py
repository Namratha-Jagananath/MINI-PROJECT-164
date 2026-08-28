"""
Distributed Crawler Module (M2)

Responsibility:
    Connect through Tor to visit candidate addresses concurrently across
    multiple worker nodes, follow discovered links, and record page
    metadata for downstream deduplication and storage.

Status: SCAFFOLD — interfaces only, implementation pending (Week 6-8).

Note: this module should be built and operated within the team's
institutional/ethics-review guidelines for security research, and should
respect target-service availability (rate limiting, backoff) rather than
attempt to defeat access controls.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CrawlResult:
    url: str
    status: str  # e.g. "reachable", "unreachable", "timeout"
    content_hash: Optional[str] = None
    fetched_at: Optional[str] = None


class TorCrawlWorker:
    """A single crawl worker operating over a Tor SOCKS proxy connection."""

    def __init__(self, worker_id: str, tor_socks_proxy: str = "socks5h://127.0.0.1:9050"):
        self.worker_id = worker_id
        self.tor_socks_proxy = tor_socks_proxy

    def fetch(self, url: str) -> CrawlResult:
        """Fetch a single .onion URL through the configured Tor proxy.

        TODO: implement request handling, timeouts, and retry/backoff policy.
        """
        raise NotImplementedError

    def extract_links(self, html: str) -> List[str]:
        """Extract outbound .onion links discovered on a fetched page.

        TODO: implement HTML parsing and link normalization.
        """
        raise NotImplementedError


class CrawlerPool:
    """Coordinates a pool of TorCrawlWorker instances across a queue of seeds."""

    def __init__(self, workers: List[TorCrawlWorker]):
        self.workers = workers

    def run(self, seed_urls: List[str]) -> List[CrawlResult]:
        """Distribute seed_urls across workers and collect CrawlResult objects.

        TODO: implement concurrency/queueing (e.g. asyncio or Scrapy) and
        graceful handling of unreachable/slow services.
        """
        raise NotImplementedError
