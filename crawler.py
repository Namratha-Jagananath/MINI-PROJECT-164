import hashlib
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


@dataclass
class CrawlResult:
    url: str
    status: str
    content_hash: Optional[str]
    content_text: Optional[str] = None
    fetched_at: str = ""


class TorCrawlWorker:
    """
    Worker that fetches .onion URLs through the Tor SOCKS proxy.

    Local:
        127.0.0.1:9050

    Docker:
        host.docker.internal:9050
    """

    def __init__(
        self,
        worker_id: int = 1,
        timeout: int = 30,
        max_retries: int = 2,
        backoff_seconds: float = 1.0,
    ):
        self.worker_id = worker_id
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

        tor_host = os.getenv("TOR_PROXY_HOST", "127.0.0.1")
        tor_port = os.getenv("TOR_PROXY_PORT", "9050")

        self.tor_host = tor_host
        self.tor_port = tor_port

        self.proxies = {
            "http": f"socks5h://{tor_host}:{tor_port}",
            "https": f"socks5h://{tor_host}:{tor_port}",
        }

    def _is_onion_url(self, url: str) -> bool:
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

        fetched_at = datetime.now(timezone.utc).isoformat()

        print(
            f"[Worker {self.worker_id}] Starting: {url}",
            flush=True
        )

        if not self._is_onion_url(url):

            print(
                f"[Worker {self.worker_id}] Invalid onion URL",
                flush=True
            )

            return CrawlResult(
                url=url,
                status="invalid_url",
                content_hash=None,
                content_text=None,
                fetched_at=fetched_at,
            )

        last_error = None

        for attempt in range(self.max_retries + 1):

            try:

                response = requests.get(
                    url,
                    proxies=self.proxies,
                    timeout=self.timeout,
                    allow_redirects=True,
                )

                response.raise_for_status()

                content_hash = hashlib.sha256(
                    response.content
                ).hexdigest()

                soup = BeautifulSoup(
                    response.text,
                    "html.parser"
                )

                content_text = soup.get_text(
                    separator=" ",
                    strip=True
                )

                print(
                    f"[Worker {self.worker_id}] "
                    f"Success: {url} "
                    f"Status={response.status_code}",
                    flush=True
                )

                return CrawlResult(
                    url=url,
                    status="reachable",
                    content_hash=content_hash,
                    content_text=content_text,
                    fetched_at=fetched_at,
                )

            except requests.RequestException as error:

                last_error = str(error)

                print(
                    f"[Worker {self.worker_id}] "
                    f"Attempt {attempt + 1} failed: "
                    f"{last_error}",
                    flush=True
                )

                if attempt < self.max_retries:

                    time.sleep(
                        self.backoff_seconds * (attempt + 1)
                    )

        print(
            f"[Worker {self.worker_id}] "
            f"Unreachable: {url}",
            flush=True
        )

        return CrawlResult(
            url=url,
            status="unreachable",
            content_hash=None,
            content_text=None,
            fetched_at=fetched_at,
        )


class CrawlerPool:

    def __init__(self, workers: List[TorCrawlWorker]):
        self.workers = workers

    def run(self, seed_urls: List[str]) -> List[CrawlResult]:

        if not self.workers or not seed_urls:
            return []

        worker_count = min(
            len(self.workers),
            len(seed_urls)
        )

        print(
            f"\n[M2] Starting concurrent crawl "
            f"with {worker_count} workers",
            flush=True
        )

        results = [None] * len(seed_urls)

        with ThreadPoolExecutor(
            max_workers=worker_count
        ) as executor:

            future_map = {}

            for index, url in enumerate(seed_urls):

                worker = self.workers[
                    index % len(self.workers)
                ]

                future = executor.submit(
                    worker.fetch,
                    url
                )

                future_map[future] = index

            for future in as_completed(future_map):

                index = future_map[future]

                try:
                    results[index] = future.result()

                except Exception as error:

                    print(
                        f"[M2] Worker error: {error}",
                        flush=True
                    )

        return [
            result
            for result in results
            if result is not None
        ]

    def extract_links(
        self,
        content: str
    ) -> List[str]:

        soup = BeautifulSoup(
            content,
            "html.parser"
        )

        links = []

        for anchor in soup.find_all(
            "a",
            href=True
        ):

            href = anchor.get("href")

            if href and self._is_onion_link(href):
                links.append(href)

        return sorted(set(links))

    @staticmethod
    def _is_onion_link(url: str) -> bool:

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


if __name__ == "__main__":

    print("=" * 60)
    print("TOR CONCURRENT CRAWLER MODULE TEST")
    print("=" * 60)

    base_url = (
        "http://"
        "lumz6w62s6jhdqpzbk35xlvcr25in7cgl3mjb5e5z5wi2u3x6me5w3yd"
        ".onion"
    )

    test_urls = [
        base_url + "/",
        base_url + "/page1.html",
        base_url + "/page2.html",
    ]

    workers = [
        TorCrawlWorker(worker_id=1),
        TorCrawlWorker(worker_id=2),
        TorCrawlWorker(worker_id=3),
    ]

    pool = CrawlerPool(workers)

    print("\nURLs to crawl:")

    for url in test_urls:
        print(" -", url)

    results = pool.run(test_urls)

    print("\n" + "=" * 60)
    print("CRAWL RESULTS")
    print("=" * 60)

    for result in results:

        print("\nURL:", result.url)
        print("Status:", result.status)
        print("Content Hash:", result.content_hash)
        print("Content:", result.content_text)
        print("Fetched At:", result.fetched_at)

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
