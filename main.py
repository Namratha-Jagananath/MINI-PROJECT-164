"""
Main Application Pipeline

Modules:

M1 - Multi-Channel Seed Acquisition
M2 - Distributed/Concurrent Tor Crawler
M3 - ML-Based Deduplication
M4 - Continuous Liveness
M5 - Cloud/Local Orchestration
M6 - SQLite Storage
"""

from urllib.parse import urlparse

from seed_acquisition import SeedAcquisitionManager
from orchestration import Orchestrator, WorkerPoolConfig
from deduplication import DeduplicationEngine
from liveness_check import LivenessChecker
from storage import DataStore, ServiceRecord


AUTHORIZED_TARGETS_FILE = "authorized_targets.txt"
THREAT_INTEL_FEED_FILE = "threat_intel_feed.txt"
DATABASE_FILE = "tor_services.db"


def run_pipeline():

    print("=" * 60)
    print("        TOR HIDDEN SERVICE ENUMERATION PIPELINE")
    print("=" * 60)

    # ============================================================
    # M1 - MULTI-CHANNEL SEED ACQUISITION
    # ============================================================

    print("\n[M1] MULTI-CHANNEL SEED ACQUISITION")
    print("-" * 40)

    manager = SeedAcquisitionManager()

    # ------------------------------------------------------------
    # Channel 1: Local seed file
    # ------------------------------------------------------------

    manager.acquire_from_file("seeds.txt")

    # ------------------------------------------------------------
    # Channel 2: Public discovery source
    # ------------------------------------------------------------

    public_source = "https://onion.torproject.org/"
    manager.acquire_from_public_source(public_source)

    # ------------------------------------------------------------
    # Channel 3: Threat-intelligence feed
    # ------------------------------------------------------------

    manager.acquire_from_threat_feed(
        THREAT_INTEL_FEED_FILE
    )

    # All discovered candidates
    all_seeds = manager.get_seeds()

    # Only explicitly authorized targets can be crawled
    authorized_seeds = manager.get_authorized_seeds(
        AUTHORIZED_TARGETS_FILE
    )

    print("\nM1 SUMMARY")
    print("-" * 40)

    print(
        "Total valid candidates:",
        len(all_seeds)
    )

    print(
        "Authorized crawl targets:",
        len(authorized_seeds)
    )

    for seed in authorized_seeds:
        print(
            "Authorized:",
            seed.url
        )

    # ============================================================
    # M5 - ORCHESTRATION
    # ============================================================

    print("\n[M5] ORCHESTRATION")
    print("-" * 40)

    config = WorkerPoolConfig(
        min_workers=1,
        max_workers=3,
        target_queue_depth_per_worker=1
    )

    orchestrator = Orchestrator(config)

    authorized_urls = [
        seed.url
        for seed in authorized_seeds
    ]

    print(
        "Authorized crawl queue:",
        len(authorized_urls)
    )

    if authorized_urls:

        orchestrator.set_queue_depth(
            len(authorized_urls)
        )

        worker_count = orchestrator.scale()

        print(
            "Workers selected:",
            worker_count
        )

    else:

        worker_count = 0

        print(
            "Workers selected: 0"
        )

    # ============================================================
    # M2 - CONCURRENT TOR CRAWLER
    # ============================================================

    print("\n[M2] TOR CRAWLER")
    print("-" * 40)

    crawl_results = []

    if authorized_urls:

        crawl_results = orchestrator.crawl(
            authorized_urls
        )

    else:

        print(
            "No authorized URLs available for crawling."
        )

    print(
        "\nCrawl results:",
        len(crawl_results)
    )

    for result in crawl_results:

        print("\n----------------------------------------")

        print(
            "URL:",
            result.url
        )

        print(
            "Status:",
            result.status
        )

        print(
            "Content Hash:",
            result.content_hash
        )

        if result.content_text:

            print(
                "Content available: True"
            )

        else:

            print(
                "Content available: False"
            )

    # Create URL → crawl result mapping
    crawl_map = {
        result.url: result
        for result in crawl_results
    }

    # ============================================================
    # M3 - ML DEDUPLICATION
    # ============================================================

    print("\n[M3] ML DEDUPLICATION")
    print("-" * 40)

    deduplication = DeduplicationEngine()

    candidates_with_content = 0
    candidates_without_content = 0

    unique_pages = 0
    exact_duplicates = 0
    near_duplicates = 0

    # ------------------------------------------------------------
    # Group crawl results by hostname.
    #
    # M1 stores candidates at host level:
    #     http://example.onion
    #
    # M2 stores exact authorized URLs:
    #     http://example.onion/
    #     http://example.onion/page1.html
    #     http://example.onion/page2.html
    #
    # Therefore M3 matches them using the hostname.
    # ------------------------------------------------------------

    crawl_results_by_host = {}

    for result in crawl_results:

        result_host = urlparse(
            result.url
        ).hostname

        if result_host is None:
            continue

        result_host = result_host.lower()

        if result_host not in crawl_results_by_host:
            crawl_results_by_host[result_host] = []

        crawl_results_by_host[result_host].append(
            result
        )

    # ------------------------------------------------------------
    # Process all M1 candidates.
    #
    # Unauthorized candidates are NOT crawled.
    # Only candidates whose hostname has authorized crawl
    # results receive content for ML processing.
    # ------------------------------------------------------------

    for index, seed in enumerate(
        all_seeds,
        start=1
    ):

        print("\n----------------------------------------")

        print(
            f"M3 Candidate {index} / "
            f"{len(all_seeds)}"
        )

        print(
            "URL:",
            seed.url
        )

        print(
            "Source:",
            seed.source
        )

        seed_host = urlparse(
            seed.url
        ).hostname

        if seed_host is not None:
            seed_host = seed_host.lower()

        matching_results = (
            crawl_results_by_host.get(
                seed_host,
                []
            )
        )

        # --------------------------------------------------------
        # Candidate has one or more authorized crawl results
        # --------------------------------------------------------

        content_results = [
            result
            for result in matching_results
            if (
                result.status == "reachable"
                and result.content_hash
                and result.content_text
            )
        ]

        if content_results:

            # Count every authorized crawled page that contains
            # usable content.
            candidates_with_content += len(
                content_results
            )

            print(
                "Content source:",
                "Tor crawler"
            )

            print(
                "Content available:",
                "True"
            )

            print(
                "Authorized pages processed:",
                len(content_results)
            )

            # ----------------------------------------------------
            # Process each authorized page through M3.
            # ----------------------------------------------------

            for crawl_result in content_results:

                print(
                    "\n  M3 Content URL:",
                    crawl_result.url
                )

                print(
                    "  Content Hash:",
                    crawl_result.content_hash
                )

                # ------------------------------------------------
                # Exact duplicate detection
                # ------------------------------------------------

                duplicate = (
                    deduplication.check_duplicate(
                        crawl_result.url,
                        crawl_result.content_hash
                    )
                )

                if duplicate:

                    exact_duplicates += 1

                    print(
                        "  Exact duplicate detected"
                    )

                    print(
                        "  Original:",
                        duplicate.original_url
                    )

                else:

                    unique_pages += 1

                    print(
                        "  Exact duplicate:",
                        "No"
                    )

                # ------------------------------------------------
                # TF-IDF similarity detection
                # ------------------------------------------------

                similarity_result = (
                    deduplication.check_similarity(
                        crawl_result.url,
                        crawl_result.content_text
                    )
                )

                if similarity_result:
                    near_duplicates += 1

                    print(
                        "  Near-duplicate match detected"
                    )

                    print(
                        "  Similar to:",
                        similarity_result.similar_to
                    )

                    print(
                        "  Cosine similarity:",
                        round(
                            similarity_result.similarity_score,
                            4
                        )
                    )
                else:
                    print(
                        "  Near-duplicate match:",
                        "None"
                    )
        # --------------------------------------------------------
        # Candidate has no authorized crawl content
        # --------------------------------------------------------

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

    # ============================================================
    # M3 SUMMARY
    # ============================================================

    print("\n" + "=" * 40)

    print(
        "        M3 ML DEDUPLICATION SUMMARY"
    )

    print("=" * 40)

    print(
        "Total candidates processed:",
        len(all_seeds)
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
        unique_pages
    )

    print(
        "Exact duplicates:",
        exact_duplicates
    )

    print(
        "Near-duplicate pages:",
        near_duplicates
    )

    print(
        "TF-IDF similarity threshold:",
        deduplication.similarity_threshold
    )

    # ============================================================
    # M4 - LIVENESS CHECK
    # ============================================================

    print("\n[M4] LIVENESS CHECK")
    print("-" * 40)

    liveness_checker = LivenessChecker()

    liveness_results = []

    for seed in authorized_seeds:

        print("\n----------------------------------------")

        print(
            "URL:",
            seed.url
        )

        liveness_result = (
            liveness_checker.check(
                seed.url
            )
        )

        liveness_results.append(
            liveness_result
        )

        print(
            "Active:",
            liveness_result.is_active
        )

        print(
            "Status Code:",
            liveness_result.status_code
        )

        print(
            "Checked At:",
            liveness_result.last_checked_at
        )

    # ============================================================
    # M6 - SQLITE STORAGE
    # ============================================================

    print("\n[M6] SQLITE STORAGE")
    print("-" * 40)

    datastore = DataStore(
        DATABASE_FILE
    )

    stored_count = 0

    for result in crawl_results:

        service_record = ServiceRecord(
            first_seen_at=result.fetched_at,
            url=result.url,
            content_hash=result.content_hash,
            last_checked_at=result.fetched_at
        )

        datastore.add_service(
            service_record
        )

        stored_count += 1

    print(
        "Records stored:",
        stored_count
    )

    # ============================================================
    # FINAL PIPELINE SUMMARY
    # ============================================================

    print("\n" + "=" * 60)

    print(
        "              PIPELINE COMPLETE"
    )

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
    run_pipeline()
