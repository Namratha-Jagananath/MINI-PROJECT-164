"""
Multi-Channel Seed Acquisition Module (M1)

Channels:
1. Local seed file
2. Public web source
3. Threat-intelligence feed

The module:
- validates v3 .onion URLs
- normalizes URLs
- removes duplicates
- records the discovery source
- supports an authorization allowlist
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse
import re
import requests
from bs4 import BeautifulSoup


@dataclass
class Seed:
    url: str
    source: str
    discovered_at: str


class SeedAcquisitionManager:

    def __init__(self):
        self.seeds = {}

    def is_valid_onion_url(self, url):
        """Check for a valid HTTP/HTTPS v3 onion URL."""
        try:
            parsed = urlparse(url.strip())

            if parsed.scheme not in ("http", "https"):
                return False

            hostname = parsed.hostname

            if not hostname:
                return False

            hostname = hostname.lower()

            if not hostname.endswith(".onion"):
                return False

            onion_name = hostname[:-6]

            if not re.fullmatch(r"[a-z2-7]{56}", onion_name):
                return False

            return True

        except Exception:
            return False

    def normalize_url(self, url):
        """Normalize an onion URL to scheme + hostname."""
        parsed = urlparse(url.strip())

        scheme = parsed.scheme.lower()
        hostname = parsed.hostname.lower()

        return f"{scheme}://{hostname}"

    def add_seed(self, url, source):
        """Validate and add a unique seed."""
        if not self.is_valid_onion_url(url):
            return False

        normalized_url = self.normalize_url(url)

        if normalized_url in self.seeds:
            return False

        self.seeds[normalized_url] = Seed(
            url=normalized_url,
            source=source,
            discovered_at=datetime.now(timezone.utc).isoformat()
        )

        return True

    def acquire_from_file(self, filename):
        """Channel 1: Read candidate onion URLs from a local file."""
        count = 0

        try:
            with open(filename, "r") as file:
                for line in file:
                    url = line.strip()

                    if not url or url.startswith("#"):
                        continue

                    if self.add_seed(url, f"local-file:{filename}"):
                        count += 1

        except FileNotFoundError:
            print("Seed file not found:", filename)

        return count

    def acquire_from_public_source(self, source_url):
        """Channel 2: Extract candidate onion URLs from a public web source."""
        count = 0

        try:
            response = requests.get(
                source_url,
                timeout=20
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            for anchor in soup.find_all("a", href=True):
                href = anchor["href"].strip()

                if self.add_seed(
                    href,
                    f"public-source:{source_url}"
                ):
                    count += 1

        except requests.RequestException as exc:
            print("Could not access public source:", exc)

        return count

    def acquire_from_threat_feed(self, filename):
        """Channel 3: Read candidate onion URLs from a threat-intelligence feed."""
        count = 0

        try:
            with open(filename, "r") as file:
                for line in file:
                    url = line.strip()

                    if not url or url.startswith("#"):
                        continue

                    if self.add_seed(url, f"threat-intel:{filename}"):
                        count += 1

        except FileNotFoundError:
            print("Threat-intelligence feed not found:", filename)

        return count

    def get_seeds(self):
        """Return all unique Seed objects."""
        return sorted(
            self.seeds.values(),
            key=lambda seed: seed.url
        )

    def get_urls(self):
        """Return only the URLs."""
        return sorted(self.seeds.keys())

    def get_authorized_seeds(self, authorization_file):
        """Return only URLs explicitly listed in the authorization file."""

        authorized_seeds = []

        try:
            with open(authorization_file, "r") as file:
                for line in file:
                    url = line.strip()

                    if not url or url.startswith("#"):
                        continue

                    if not self.is_valid_onion_url(url):
                        continue

                    parsed = urlparse(url)

                    scheme = parsed.scheme.lower()
                    hostname = parsed.hostname.lower()
                    path = parsed.path or "/"

                    authorized_url = f"{scheme}://{hostname}{path}"

                    authorized_seeds.append(
                        Seed(
                            url=authorized_url,
                            source="authorization-file",
                            discovered_at=datetime.now(
                                timezone.utc
                            ).isoformat()
                        )
                    )

        except FileNotFoundError:
            print(
                "Authorization file not found:",
                authorization_file
            )
            return []

        # Remove duplicate authorized URLs while preserving order.
        unique_seeds = {}
        for seed in authorized_seeds:
            unique_seeds[seed.url] = seed

        return list(unique_seeds.values())


if __name__ == "__main__":

    manager = SeedAcquisitionManager()

    print("\n" + "=" * 60)
    print("       MULTI-CHANNEL SEED ACQUISITION - M1")
    print("=" * 60)

    file_count = manager.acquire_from_file("seeds.txt")

    print("\nChannel 1 - Local Seed File")
    print("New candidates:", file_count)

    public_source = "https://onion.torproject.org/"

    public_count = manager.acquire_from_public_source(
        public_source
    )

    print("\nChannel 2 - Public Web Source")
    print("New candidates:", public_count)

    threat_count = manager.acquire_from_threat_feed(
        "threat_intel_feed.txt"
    )

    print("\nChannel 3 - Threat-Intelligence Feed")
    print("New candidates:", threat_count)

    seeds = manager.get_seeds()

    print("\n" + "=" * 60)
    print("              DISCOVERY RESULTS")
    print("=" * 60)

    print("Total unique valid candidates:", len(seeds))

    for number, seed in enumerate(seeds, start=1):
        print(f"{number}. {seed.url}")
        print(f"   Source: {seed.source}")
        print(f"   Discovered: {seed.discovered_at}")

    authorized = manager.get_authorized_seeds(
        "authorized_targets.txt"
    )

    print("\n" + "=" * 60)
    print("             AUTHORIZED TARGETS")
    print("=" * 60)

    print(
        "Authorized seeds ready for crawling:",
        len(authorized)
    )

    for number, seed in enumerate(authorized, start=1):
        print(f"{number}. {seed.url}")

    print("\n" + "=" * 60)