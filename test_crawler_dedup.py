"""
M2 + M3 Integration Test

Tests:
M2 - Tor crawler
M3 - Exact duplicate detection
M3 - Similar-page detection
"""

from crawler import TorCrawlWorker
from deduplication import DeduplicationEngine


# --------------------------------------------------
# AUTHORIZED CONTROLLED TEST TARGET
# --------------------------------------------------

TARGET_URL = (
    "http://lumz6w62s6jhdqpzbk35xlvcr25in7cgl3mjb5e5z5wi2u3x6me5w3yd.onion"
)


# --------------------------------------------------
# START
# --------------------------------------------------

print("========================================")
print("       M2 + M3 INTEGRATION TEST")
print("========================================")


# --------------------------------------------------
# M2 - TOR CRAWLER
# --------------------------------------------------

print("\n[M2] Starting crawler...")

crawler = TorCrawlWorker(worker_id=1)

print("[M2] Crawling controlled target:")
print(TARGET_URL)

result = crawler.fetch(TARGET_URL)

print("\n[M2] Crawl Result")
print("----------------------------")
print("URL:", result.url)
print("Status:", result.status)
print("Content Hash:", result.content_hash)
print("Fetched At:", result.fetched_at)


# --------------------------------------------------
# M3 - DEDUPLICATION
# --------------------------------------------------

print("\n[M3] Starting deduplication...")

deduplication = DeduplicationEngine(
    similarity_threshold=0.80
)


# --------------------------------------------------
# EXACT DUPLICATE CHECK
# --------------------------------------------------

if result.status == "reachable":

    duplicate = deduplication.check_duplicate(
        result.url,
        result.content_hash
    )

    if duplicate:

        print("\n[M3] Exact duplicate detected")
        print("Duplicate URL:", duplicate.url)
        print("Original URL:", duplicate.duplicate_of)
        print("Content Hash:", duplicate.content_hash)

    else:

        print("\n[M3] Page is unique")

else:

    print("\n[M3] Deduplication skipped")
    print("Reason: page was not reachable")


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

print("\n[M3] Deduplication Summary")
print("----------------------------")
print("Unique pages:", deduplication.count_unique())
print("Exact duplicates:", deduplication.count_duplicates())
print("Similar pages:", deduplication.count_similar_pages())


# --------------------------------------------------
# COMPLETE
# --------------------------------------------------

print("\n========================================")
print("      INTEGRATION TEST COMPLETE")
print("========================================")
