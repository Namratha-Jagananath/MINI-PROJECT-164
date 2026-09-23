"""
Distributed Crawler Module (M2)

Safe Tor-based crawler for authorized security research.

Features:
- Fetches .onion URLs through the local Tor SOCKS proxy
- Uses timeouts and retry/backoff
- Calculates content hashes
- Extracts .onion links from HTML
- Supports multiple workers
"""

from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import time

import requests
from bs4 import BeautifulSoup


@dataclass
class CrawlResult:
    url: str
    status: str
    content_hash: Optional[str] = None
    fetched_at: Optional[str] = None


class TorCrawlWorker:
    """A single crawl worker operating through a Tor SOCKS proxy."""

    def __init__(
        self,
        worker_id: str,
        tor_socks_proxy: str = "socks5h://127.0.0.1:9050",
        timeout: int = 20,
        max_retries: int = 2,
        delay: float = 1.0,
    ):
        self.worker_id = worker_id
        self.tor_socks_proxy = tor_socks_proxy
        self.timeout = timeout
        self.max_retries = max_retries
        self.delay = delay

        self.session = requests.Session()

        self.session.proxies.update({
            "http": self.tor_socks_proxy,
            "https": self.tor_socks_proxy,
        })

        self.session.headers.update({
            "User-Agent": "Authorized-Tor-Research-Crawler/1.0"
        })

    def _is_onion_url(self, url: str) -> bool:
        """Allow only HTTP/HTTPS .onion URLs."""

        try:
            parsed = urlparse(url)

            if parsed.scheme not in ("http", "https"):
                return False

            hostname = parsed.hostname

            if not hostname:
                return False

            return hostname.lower().endswith(".onion")

        except Exception:
            return False

    def fetch(self, url: str) -> CrawlResult:
        """
        Fetch a single .onion URL through Tor.

        Uses timeout, retry and exponential backoff.
        """

        fetched_at = datetime.now(timezone.utc).isoformat()

        if not self._is_onion_url(url):
            return CrawlResult(
                url=url,
                status="invalid_url",
                fetched_at=fetched_at,
            )

        last_status = "unreachable"

        for attempt in range(self.max_retries + 1):

            try:
                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    allow_redirects=True,
                )

                response.raise_for_status()

                content_hash = hashlib.sha256(
                    response.content
                ).hexdigest()

                return CrawlResult(
                    url=url,
                    status="reachable",
                    content_hash=content_hash,
                    fetched_at=fetched_at,
                )

            except requests.exceptions.Timeout:
                last_status = "timeout"

            except requests.exceptions.RequestException:
                last_status = "unreachable"

            if attempt < self.max_retries:
                time.sleep(self.delay * (2 ** attempt))

        return CrawlResult(
            url=url,
            status=last_status,
            fetched_at=fetched_at,
        )

    def extract_links(self, html: str) -> List[str]:
        """
        Extract HTTP/HTTPS .onion links from HTML.

        Relative links are resolved against the page URL when a base
        URL is supplied separately by the caller.
        """

        soup = BeautifulSoup(html, "html.parser")

        links = set()

        for anchor in soup.find_all("a", href=True):

            href = anchor.get("href", "").strip()

            if not href:
                continue

            parsed = urlparse(href)

            if parsed.scheme not in ("http", "https"):
                continue

            hostname = parsed.hostname

            if hostname and hostname.lower().endswith(".onion"):
                links.add(href)

        return sorted(links)


class CrawlerPool:
    """Coordinates multiple Tor crawler workers."""

    def __init__(self, workers: List[TorCrawlWorker]):
        self.workers = workers

    def run(self, seed_urls: List[str]) -> List[CrawlResult]:
        """
        Distribute seed URLs across workers and collect results.
        """

        if not self.workers or not seed_urls:
            return []

        results = []

        with ThreadPoolExecutor(
            max_workers=len(self.workers)
        ) as executor:

            futures = []

            for index, url in enumerate(seed_urls):
                worker = self.workers[index % len(self.workers)]

                futures.append(
                    executor.submit(worker.fetch, url)
                )

            for future in as_completed(futures):

                try:
                    results.append(future.result())

                except Exception as exc:
                    results.append(
                        CrawlResult(
                            url="unknown",
                            status=f"error: {type(exc).__name__}",
                            fetched_at=datetime.now(
                                timezone.utc
                            ).isoformat(),
                        )
                    )

        return results
