"""
Main Application

Efficient Enumeration of URLs of Active Hidden Servers
over Anonymous Channel (TOR)

Runs the complete authorized pipeline:

M1 - Seed Acquisition
M5 - Orchestration
M2 - Tor Crawler
M3 - Deduplication
M4 - Liveness
M6 - Storage
"""

from seed_acquisition import SeedAcquisitionManager
from orchestration import Orchestrator, WorkerPoolConfig
from deduplication import DeduplicationEngine
from liveness_check import LivenessChecker
from storage import DataStore, ServiceRecord


AUTHORIZED_TARGETS_FILE = "authorized_targets.txt"
THREAT_INTEL_FEED_FILE = "threat_intel_feed.txt"
DATABASE_FILE = "tor_services.db"


def main():

    print("=" * 60)
    print("   TOR HIDDEN SERVICE ENUMERATION SYSTEM")
    print("=" * 60)

    # ----------------------------------------
    # M1 - Seed Acquisition
    # ----------------------------------------

    print("\n[M1] SEED ACQUISITION")
    print("-" * 40)

    manager = SeedAcquisitionManager()

    local_count = manager.acquire_from_file(
        "seeds.txt"
    )

    print("Channel 1 - Local Seed File")
    print("New candidates:", local_count)

    public_count = manager.acquire_from_public_source(
        "https://onion.torproject.org/"
    )

    print("Channel 2 - Public Web Source")
    print("New candidates:", public_count)

    threat_count = manager.acquire_from_threat_feed(
        THREAT_INTEL_FEED_FILE
    )

    print("Channel 3 - Threat-Intelligence Feed")
    print("New candidates:", threat_count)

    all_seeds = manager.get_seeds()

    print("Total valid candidates:", len(all_seeds))

    seeds = manager.get_authorized_seeds(
        AUTHORIZED_TARGETS_FILE
    )

    print("Authorized seeds for crawling:", len(seeds))

    if not seeds:
        print("No authorized targets found.")
        return

    for seed in seeds:
        print("Authorized Seed:", seed)

    # ----------------------------------------
    # M5 - Orchestration
    # ----------------------------------------

    print("\n[M5] ORCHESTRATION")
    print("-" * 40)

    config = WorkerPoolConfig(
        min_workers=1,
        max_workers=3,
        target_queue_depth_per_worker=2
    )

    orchestrator = Orchestrator(config)

    orchestrator.set_queue_depth(len(seeds))

    worker_count = orchestrator.scale()

    print("Queue depth:", orchestrator.current_queue_depth())
    print("Workers selected:", worker_count)

    # ----------------------------------------
    # M2 - Tor Crawler
    # ----------------------------------------

    print("\n[M2] TOR CRAWLER")
    print("-" * 40)

    crawl_results = orchestrator.crawl([seed.url for seed in seeds])

    for result in crawl_results:

        print("\nURL:", result.url)
        print("Status:", result.status)
        print("Content Hash:", result.content_hash)
        print("Fetched At:", result.fetched_at)

    # ----------------------------------------
    # M3 - Deduplication
    # ----------------------------------------

    print("\n[M3] DEDUPLICATION")
    print("-" * 40)

    deduplication = DeduplicationEngine(
        similarity_threshold=0.80
    )

    duplicate_map = {}

    for result in crawl_results:

        if result.status != "reachable":
            continue

        duplicate = deduplication.check_duplicate(
            result.url,
            result.content_hash
        )

        if duplicate:

            duplicate_map[result.url] = duplicate.duplicate_of

            print("Duplicate:", result.url)
            print("Original:", duplicate.duplicate_of)

        else:

            print("Unique:", result.url)

    print("\nUnique pages:", deduplication.count_unique())
    print(
        "Exact duplicates:",
        deduplication.count_duplicates()
    )

    # ----------------------------------------
    # M4 - Liveness
    # ----------------------------------------

    print("\n[M4] LIVENESS CHECK")
    print("-" * 40)

    liveness_checker = LivenessChecker()

    liveness_results = {}

    for seed in seeds:

        result = liveness_checker.check(seed.url)

        liveness_results[result.url] = result

        print("\nURL:", result.url)
        print("Active:", result.is_active)
        print("Status Code:", result.status_code)
        print("Checked At:", result.last_checked_at)

    # ----------------------------------------
    # M6 - Storage
    # ----------------------------------------

    print("\n[M6] SQLITE STORAGE")
    print("-" * 40)

    store = DataStore(DATABASE_FILE)

    for crawl_result in crawl_results:

        liveness_result = liveness_results.get(
            crawl_result.url
        )

        duplicate_of = duplicate_map.get(
            crawl_result.url
        )

        record = ServiceRecord(
            url=crawl_result.url,
            first_seen_at=crawl_result.fetched_at,
            last_checked_at=(
                liveness_result.last_checked_at
                if liveness_result
                else None
            ),
            is_active=(
                liveness_result.is_active
                if liveness_result
                else None
            ),
            content_hash=crawl_result.content_hash,
            is_mirror_of=duplicate_of,
            source="authorized-target"
        )

        store.add_service(record)

    print("Records stored:", store.count_services())

    store.close()

    # ----------------------------------------
    # Completion
    # ----------------------------------------

    print("\n" + "=" * 60)
    print("             PIPELINE COMPLETE")
    print("=" * 60)

    print("M1 Seed Acquisition : SUCCESS")
    print("M2 Tor Crawler      : SUCCESS")
    print("M3 Deduplication    : SUCCESS")
    print("M4 Liveness         : SUCCESS")
    print("M5 Orchestration    : SUCCESS")
    print("M6 Storage          : SUCCESS")

    print("=" * 60)


if __name__ == "__main__":
    main()
