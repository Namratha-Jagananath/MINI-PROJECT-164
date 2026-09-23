"""
Liveness Checking Module (M4)

Checks whether an authorized .onion service is reachable
through the local Tor SOCKS proxy.
"""

from dataclasses import dataclass
from datetime import datetime, timezone

import requests


@dataclass
class LivenessRecord:
    url: str
    is_active: bool
    status_code: int | None
    last_checked_at: str


class LivenessChecker:
    def __init__(
        self,
        tor_socks_proxy="socks5h://127.0.0.1:9050",
        timeout=20,
    ):
        self.tor_socks_proxy = tor_socks_proxy
        self.timeout = timeout

        self.session = requests.Session()

        self.session.proxies.update({
            "http": self.tor_socks_proxy,
            "https": self.tor_socks_proxy,
        })

        self.session.headers.update({
            "User-Agent": "Authorized-Tor-Liveness-Checker/1.0"
        })

    def check(self, url):
        """Check whether the .onion URL is currently reachable."""

        checked_at = datetime.now(timezone.utc).isoformat()

        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
            )

            return LivenessRecord(
                url=url,
                is_active=response.status_code < 400,
                status_code=response.status_code,
                last_checked_at=checked_at,
            )

        except requests.RequestException:

            return LivenessRecord(
                url=url,
                is_active=False,
                status_code=None,
                last_checked_at=checked_at,
            )


if __name__ == "__main__":

    url = (
        "http://"
        "lumz6w62s6jhdqpzbk35xlvcr25in7cgl3mjb5e5z5wi2u3x6me5w3yd"
        ".onion"
    )

    checker = LivenessChecker()

    result = checker.check(url)

    print("\n===== LIVENESS CHECK =====\n")

    print("URL:", result.url)
    print("Active:", result.is_active)
    print("Status Code:", result.status_code)
    print("Checked At:", result.last_checked_at)
