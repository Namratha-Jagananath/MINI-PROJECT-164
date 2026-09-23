"""
M1 + M2 Integration Test

M1 - Seed acquisition from authorized_targets.txt
M2 - Tor crawler
"""

from seed_acquisition import SeedAcquisitionManager
from crawler import TorCrawlWorker


print("========================================")
print("       M1 + M2 INTEGRATION TEST")
print("========================================")


# ----------------------------------------
# M1 - Seed Acquisition
# ----------------------------------------

print("\n[M1] SEED ACQUISITION")
print("----------------------------")

manager = SeedAcquisitionManager()

new_seeds = manager.acquire_from_file("authorized_targets.txt")

print("New authorized seeds:", new_seeds)

seeds = manager.get_seeds()

print("Total valid seeds:", len(seeds))

for seed in seeds:
    print("Seed:", seed)


# ----------------------------------------
# M2 - Tor Crawler
# ----------------------------------------

print("\n[M2] TOR CRAWLER")
print("----------------------------")

crawler = TorCrawlWorker(
    worker_id=1,
    timeout=10,
    max_retries=1
)

for seed in seeds:

    print("\nCrawling:", seed)

    result = crawler.fetch(seed)

    print("Status:", result.status)
    print("Content Hash:", result.content_hash)
    print("Fetched At:", result.fetched_at)


# ----------------------------------------
# Completion
# ----------------------------------------

print("\n========================================")
print("      M1 + M2 INTEGRATION COMPLETE")
print("========================================")
