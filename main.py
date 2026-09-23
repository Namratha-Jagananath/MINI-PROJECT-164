"""
Main Application

Efficient Enumeration of URLs of Active Hidden Servers
over Anonymous Channel (TOR)

Pipeline:

M1 - Multi-Channel Seed Acquisition
M5 - Orchestration
M2 - Authorized Tor Crawler
M3 - ML-Based Deduplication
M4 - Continuous Liveness
M6 - Storage / Reporting
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
    print("      TOR HIDDEN SERVICE ENUMERATION SYSTEM")
    print("=" * 60)

    # ========================================================
    # M1 - MULTI-CHANNEL SEED ACQUISITION
    # ========================================================

    print("\n[M1] SEED ACQUISITION")
    print("-" * 40)

    manager = SeedAcquisitionManager()

    # Channel 1 - Local seed file
    local_count = manager.acquire_from_file(
        "seeds.txt"
    )

    print("Channel 1 - Local Seed File")
    print("New candidates:", local_count)

    # Channel 2 - Public web source
    public_count = manager.acquire_from_public_source(
        "https://onion.torproject.org/"
    )

    print("Channel 2 - Public Web Source")
    print("New candidates:", public_count)

    # Channel 3 - Threat intelligence feed
    threat_count = manager.acquire_from_threat_feed(
        THREAT_INTEL_FEED_FILE
    )

    print("Channel 3 - Threat-Intelligence Feed")
    print("New candidates:", threat_count)

    # ALL candidates
    all_seeds = manager.get_seeds()

    print("\nTotal valid candidates:", len(all_seeds))

    # Only authorized targets can be actually crawled
    authorized_seeds = manager.get_authorized_seeds(
        AUTHORIZED_TARGETS_FILE
    )

    print(
        "Authorized seeds for crawling:",
        len(authorized_seeds)
    )

    for seed in authorized_seeds:

        print(
            "Authorized Seed:",
            seed.url
        )

    # ========================================================
    # M5 - ORCHESTRATION
    # ========================================================

    print("\n[M5] ORCHESTRATION")
    print("-" * 40)

    config = WorkerPoolConfig(
        min_workers=1,
        max_workers=3,
        target_queue_depth_per_worker=2
    )

    orchestrator = Orchestrator(config)

    # M5 scales according to actual authorized crawl queue
    orchestrator.set_queue_depth(
        len(authorized_seeds)
    )

    worker_count = orchestrator.scale()

    print(
        "Authorized crawl queue:",
        orchestrator.current_queue_depth()
    )

    print(
        "Workers selected:",
        worker_count
    )

    # ========================================================
    # M2 - TOR CRAWLER
    # ========================================================

    print("\n[M2] TOR CRAWLER")
    print("-" * 40)

    # IMPORTANT:
    # Only authorized URLs are sent to the real Tor crawler.
    authorized_urls = [
        seed.url
        for seed in authorized_seeds
    ]

    crawl_results = orchestrator.crawl(
        authorized_urls
    )

    print(
        "Authorized URLs submitted to crawler:",
        len(authorized_urls)
    )

    for result in crawl_results:

        print("\nURL:", result.url)
        print("Status:", result.status)
        print(
            "Content Hash:",
            result.content_hash
        )
        print(
            "Content Available:",
            result.content_text is not None
        )
        print(
            "Fetched At:",
            result.fetched_at
        )

    # ========================================================
    # M3 - ML-BASED DEDUPLICATION
    # ========================================================

    print("\n[M3] ML-BASED DEDUPLICATION")
    print("-" * 40)

    deduplication = DeduplicationEngine(
        similarity_threshold=0.80
    )

    duplicate_map = {}

    processed_candidates = 0
    candidates_with_content = 0
    candidates_without_content = 0

    # Map crawl results by URL
    crawl_map = {
        result.url: result
        for result in crawl_results
    }

    print(
        "Candidates entering M3:",
        len(all_seeds)
    )

    # --------------------------------------------------------
    # ALL 66 CANDIDATES ENTER M3
    # --------------------------------------------------------

    for seed in all_seeds:

        processed_candidates += 1

        print("\n----------------------------------------")
        print(
            "M3 Candidate",
            processed_candidates,
            "/",
            len(all_seeds)
        )
        print("URL:", seed.url)
        print("Source:", seed.source)

        crawl_result = crawl_map.get(
            seed.url
        )

        # ----------------------------------------------------
        # REAL CRAWLED CONTENT
        # ----------------------------------------------------

        if (
            crawl_result is not None
            and crawl_result.status == "reachable"
            and crawl_result.content_hash
            and crawl_result.content_text
        ):

            candidates_with_content += 1

            print(
                "Content source:",
                "Authorized Tor crawl"
            )

            # 1. Exact duplicate detection
            duplicate = deduplication.check_duplicate(
                crawl_result.url,
                crawl_result.content_hash
            )

            if duplicate:

                duplicate_map[
                    crawl_result.url
                ] = duplicate.duplicate_of

                print(
                    "Exact duplicate:",
                    "YES"
                )

                print(
                    "Duplicate of:",
                    duplicate.duplicate_of
                )

            else:

                print(
                    "Exact duplicate:",
                    "NO"
                )

            # 2. TF-IDF + cosine similarity
            similarity_results = (
                deduplication.check_similarity(
                    crawl_result.url,
                    crawl_result.content_text
                )
            )

            if similarity_results:

                for record in similarity_results:

                    print(
                        "ML near-duplicate:",
                        "YES"
                    )

                    print(
                        "Similar to:",
                        record.similar_to
                    )

                    print(
                        "Cosine similarity:",
                        record.similarity_score
                    )

            else:

                print(
                    "ML near-duplicate:",
                    "NO"
                )

        # ----------------------------------------------------
        # NO CONTENT AVAILABLE
        # ----------------------------------------------------

        else:

            candidates_without_content += 1

            print(
                "Content source:",
                "Not available"
            )

            print(
                "ML status:",
                "Candidate registered; "
                "content unavailable"
            )

    # --------------------------------------------------------
    # M3 SUMMARY
    # --------------------------------------------------------

    print("\n========================================")
    print("        M3 ML DEDUPLICATION SUMMARY")
    print("========================================")

    print(
        "Total candidates processed:",
        processed_candidates
    )

    print(
        "Candidates with content:",
        candidates_with_content
    )

    print(
        "Candidates without content:",
        candidates_without_content
    )

    print(
        "Unique pages:",
        deduplication.count_unique()
    )

    print(
        "Exact duplicates:",
        deduplication.count_duplicates()
    )

    print(
        "Near-duplicate pages:",
        deduplication.count_similar_pages()
    )

    print(
        "TF-IDF similarity threshold:",
        deduplication.similarity_threshold
    )

    # ========================================================
    # M4 - LIVENESS CHECK
    # ========================================================

    print("\n[M4] LIVENESS CHECK")
    print("-" * 40)

    liveness_checker = LivenessChecker()

    liveness_results = {}

    # Liveness is also restricted to authorized targets
    for seed in authorized_seeds:

        result = liveness_checker.check(
            seed.url
        )

        liveness_results[
            result.url
        ] = result

        print("\nURL:", result.url)

        print(
            "Active:",
            result.is_active
        )

        print(
            "Status Code:",
            result.status_code
        )

        print(
            "Checked At:",
            result.last_checked_at
        )

    # ========================================================
    # M6 - SQLITE STORAGE
    # ========================================================

    print("\n[M6] SQLITE STORAGE")
    print("-" * 40)

    store = DataStore(
        DATABASE_FILE
    )

    for crawl_result in crawl_results:

        liveness_result = (
            liveness_results.get(
                crawl_result.url
            )
        )

        duplicate_of = (
            duplicate_map.get(
                crawl_result.url
            )
        )

        record = ServiceRecord(

            url=crawl_result.url,

            first_seen_at=(
                crawl_result.fetched_at
            ),

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

            content_hash=(
                crawl_result.content_hash
            ),

            is_mirror_of=(
                duplicate_of
            ),

            source="authorized-target"
        )

        store.add_service(record)

    print(
        "Records stored:",
        store.count_services()
    )

    store.close()

    # ========================================================
    # COMPLETION
    # ========================================================

    print("\n" + "=" * 60)
    print("             PIPELINE COMPLETE")
    print("=" * 60)

    print(
        "M1 Seed Acquisition : SUCCESS"
    )

    print(
        "M2 Tor Crawler      : SUCCESS"
    )

    print(
        "M3 ML Deduplication : SUCCESS"
    )

    print(
        "M4 Liveness         : SUCCESS"
    )

    print(
        "M5 Orchestration    : SUCCESS"
    )

    print(
        "M6 Storage          : SUCCESS"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
