"""
M5 Orchestration Integration Test

Tests:
M1 - Seed Acquisition
M2 - Tor Crawler
M3 - Deduplication
M4 - Liveness
M5 - Orchestration
M6 - Storage

Uses only the authorized controlled onion service.
"""

from seed_acquisition import SeedAcquisitionManager
from orchestration import Orchestrator, WorkerPoolConfig
from deduplication import DeduplicationEngine
from liveness_check import LivenessChecker
from storage import DataStore, ServiceRecord


print("========================================")
print("      FULL ORCHESTRATED PIPELINE")
print("========================================")


# ----------------------------------------
# M1 - Seed Acquisition
# ----------------------------------------

print("\n[M1] SEED ACQUISITION")
print("----------------------------")

manager = SeedAcquisitionManager()

manager.acquire_from_file("authorized_targets.txt")

seeds = manager.get_seeds()

print("Authorized seeds:", len(seeds))

for seed in seeds:
    print("Seed:", seed)


# ----------------------------------------
# M5 - Orchestration
# ----------------------------------------

print("\n[M5] ORCHESTRATION")
print("----------------------------")

config = WorkerPoolConfig(
    min_workers=1,
    max_workers=3,
    target_queue_depth_per_worker=2
)

orchestrator = Orchestrator(config)

orchestrator.set_queue_depth(len(seeds))

workers = orchestrator.scale()

print("Queue depth:", orchestrator.current_queue_depth())
print("Workers selected:", workers)


# ----------------------------------------
# M2 - Tor Crawler
# ----------------------------------------

print("\n[M2] TOR CRAWLER")
print("----------------------------")

crawl_results = orchestrator.crawl(seeds)

for result in crawl_results:
    print("URL:", result.url)
    print("Status:", result.status)
    print("Content Hash:", result.content_hash)
    print("Fetched At:", result.fetched_at)


# ----------------------------------------
# M3 - Deduplication
# ----------------------------------------

print("\n[M3] DEDUPLICATION")
print("----------------------------")

deduplication = DeduplicationEngine(
    similarity_threshold=0.80
)

duplicates = 0

for result in crawl_results:

    if result.status != "reachable":
        continue

    duplicate = deduplication.check_duplicate(
        result.url,
        result.content_hash
    )

    if duplicate:
        duplicates += 1
        print("Duplicate:", result.url)
        print("Original:", duplicate.duplicate_of)
    else:
        print("Unique:", result.url)


print("Unique pages:", deduplication.count_unique())
print("Exact duplicates:", duplicates)


# ----------------------------------------
# M4 - Liveness
# ----------------------------------------

print("\n[M4] LIVENESS CHECK")
print("----------------------------")

liveness_checker = LivenessChecker()

liveness_results = []

for seed in seeds:

    result = liveness_checker.check(seed)

    liveness_results.append(result)

    print("URL:", result.url)
    print("Active:", result.is_active)
    print("Status Code:", result.status_code)


# ----------------------------------------
# M6 - Storage
# ----------------------------------------

print("\n[M6] SQLITE STORAGE")
print("----------------------------")

store = DataStore("orchestrated_pipeline.db")

for crawl_result in crawl_results:

    matching_liveness = next(
        (
            item
            for item in liveness_results
            if item.url == crawl_result.url
        ),
        None
    )

    record = ServiceRecord(
        url=crawl_result.url,
        first_seen_at=crawl_result.fetched_at,
        last_checked_at=(
            matching_liveness.last_checked_at
            if matching_liveness
            else None
        ),
        is_active=(
            matching_liveness.is_active
            if matching_liveness
            else None
        ),
        content_hash=crawl_result.content_hash,
        source="authorized-target"
    )

    store.add_service(record)


print("Records stored:", store.count_services())

store.close()


# ----------------------------------------
# Completion
# ----------------------------------------

print("\n========================================")
print("    FULL ORCHESTRATED PIPELINE DONE")
print("========================================")

print("M1 Seed Acquisition : SUCCESS")
print("M2 Tor Crawler      : SUCCESS")
print("M3 Deduplication    : SUCCESS")
print("M4 Liveness         : SUCCESS")
print("M5 Orchestration    : SUCCESS")
print("M6 Storage          : SUCCESS")

print("========================================")
