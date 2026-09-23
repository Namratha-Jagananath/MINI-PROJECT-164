"""
Multi-Channel Seed Acquisition Module (M1)

Channels:
1. Local seed file
2. Official/public seed source

The module validates, normalizes and removes duplicate
v3 .onion URLs.
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
        self.seeds = set()

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

            # v3 onion addresses have 56 base32 characters
            if not re.fullmatch(r"[a-z2-7]{56}", onion_name):
                return False

            return True

        except Exception:
            return False

    def normalize_url(self, url):
        """Normalize a URL."""

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

        self.seeds.add(normalized_url)

        return True

    def acquire_from_file(self, filename):
        """Channel 1: Read seeds from a local file."""

        count = 0

        try:
            with open(filename, "r") as file:

                for line in file:
                    url = line.strip()

                    if self.add_seed(url, f"file:{filename}"):
                        count += 1

        except FileNotFoundError:
            print("Seed file not found:", filename)

        return count

    def acquire_from_public_source(self, source_url):
        """Channel 2: Extract .onion URLs from a public source."""

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
                    f"public:{source_url}"
                ):
                    count += 1

        except requests.RequestException as exc:
            print("Could not access public source:", exc)

        return count

    def get_seeds(self):
        """Return all unique seeds."""

        return sorted(self.seeds)


if __name__ == "__main__":

    manager = SeedAcquisitionManager()

    print("\n========================================")
    print("       MULTI-CHANNEL SEED ACQUISITION")
    print("========================================")

    # ------------------------------------
    # CHANNEL 1: LOCAL FILE
    # ------------------------------------

    file_count = manager.acquire_from_file(
        "seeds.txt"
    )

    print("\nChannel 1 - Local File")
    print("New seeds:", file_count)

    # ------------------------------------
    # CHANNEL 2: OFFICIAL TOR PROJECT SOURCE
    # ------------------------------------

    source = "https://onion.torproject.org/"

    public_count = manager.acquire_from_public_source(
        source
    )

    print("\nChannel 2 - Official Public Source")
    print("New seeds:", public_count)

    # ------------------------------------
    # FINAL RESULTS
    # ------------------------------------

    seeds = manager.get_seeds()

    print("\n========================================")
    print("              FINAL RESULTS")
    print("========================================")

    print("Total unique valid seeds:", len(seeds))

    for number, url in enumerate(seeds, start=1):
        print(f"{number}. {url}")

    print("\n========================================")
