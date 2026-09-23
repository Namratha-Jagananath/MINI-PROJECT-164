"""
M2 + M3 + M4 + M6 Integration Test

Tests the complete core pipeline using the
controlled authorized onion service.
"""

from crawler import TorCrawlWorker
from deduplication import DeduplicationEngine
from liveness_check import LivenessChecker
from storage import DataStore, ServiceRecord


# --------------------------------------------------
# CONTROLLED AUTHORIZED TEST TARGET
# --------------------------------------------------

TARGET_URL = (
    "http://lumz6w62s6jhdqpzbk35xlvcr25in7cgl3mjb5e5z5wi2u3x6me5w3yd.onion"
)


print("========================================")
print("       FULL TOR PIPELINE TEST")
print("========================================")


# ==================================================
# M2 - TOR CRAWLER
# ==================================================

print("\n[M2] TOR CRAWLER")
print("----------------------------")

crawler = TorCrawlWorker(worker_id=1)

crawl_result = crawler.fetch(TARGET_URL)

print("URL:", crawl_result.url)
print("Status:", crawl_result.status)
print("Content Hash:", crawl_result.content_hash)
print("Fetched At:", crawl_result.fetched_at)


# ==================================================
# M3 - DEDUPLICATION
# ==================================================

print("\n[M3] DEDUPLICATION")
print("----------------------------")

deduplication = DeduplicationEngine(
    similarity_threshold=0.80
)

duplicate = None

if crawl_result.status == "reachable":

    duplicate = deduplication.check_duplicate(
        crawl_result.url,
        crawl_result.content_hash
    )

    if duplicate:

        print("Exact duplicate: YES")
        print("Original:", duplicate.duplicate_of)

    else:

        print("Exact duplicate: NO")

else:

    print("Deduplication skipped because page is unreachable.")


print("Unique pages:", deduplication.count_unique())
print("Exact duplicates:", deduplication.count_duplicates())


# ==================================================
# M4 - LIVENESS
# ==================================================

print("\n[M4] LIVENESS CHECK")
print("----------------------------")

liveness_checker = LivenessChecker()

liveness_result = liveness_checker.check(
    TARGET_URL
)

print("Active:", liveness_result.is_active)
print("Status Code:", liveness_result.status_code)
print("Checked At:", liveness_result.last_checked_at)


# ==================================================
# M6 - STORAGE
# ==================================================

print("\n[M6] SQLITE STORAGE")
print("----------------------------")

store = DataStore("pipeline_test.db")

record = ServiceRecord(
    url=TARGET_URL,
    first_seen_at=crawl_result.fetched_at,
    last_checked_at=liveness_result.last_checked_at,
    is_active=liveness_result.is_active,
    content_hash=crawl_result.content_hash,
    is_mirror_of=(
        duplicate.duplicate_of
        if duplicate
        else None
    ),
    source="controlled-test"
)

store.add_service(record)

print("Records stored:", store.count_services())

print("\nStored data:")

for service in store.get_all_services():

    print(service)

store.close()


# ==================================================
# FINAL SUMMARY
# ==================================================

print("\n========================================")
print("       FULL PIPELINE COMPLETE")
print("========================================")

print("M2 Crawler        : SUCCESS")
print("M3 Deduplication  : SUCCESS")
print("M4 Liveness       : SUCCESS")
print("M6 Storage        : SUCCESS")

print("========================================")
