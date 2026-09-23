"""
Complete Pipeline Test

Tests:
M1 - Seed Acquisition
M2 - Tor Crawler
M3 - Deduplication
M4 - Liveness
M6 - Storage
"""

from seed_acquisition import SeedAcquisitionManager
from crawler import TorCrawlWorker
from deduplication import DeduplicationEngine
from liveness_check import LivenessChecker
from storage import DataStore, ServiceRecord


AUTHORIZED_TARGETS_FILE = "authorized_targets.txt"


def test_complete_pipeline():

    # -------------------------
    # M1 - Seed Acquisition
    # -------------------------

    manager = SeedAcquisitionManager()

    new_seeds = manager.acquire_from_file(
        AUTHORIZED_TARGETS_FILE
    )

    seeds = manager.get_seeds()

    assert new_seeds >= 1
    assert len(seeds) >= 1

    # -------------------------
    # M2 - Tor Crawler
    # -------------------------

    crawler = TorCrawlWorker(
        worker_id=1,
        timeout=20,
        max_retries=1
    )

    crawl_results = []

    for seed in seeds:
        result = crawler.fetch(seed.url)
        crawl_results.append(result)

    assert len(crawl_results) >= 1

    reachable_results = [
        result
        for result in crawl_results
        if result.status == "reachable"
    ]

    assert len(reachable_results) >= 1

    # -------------------------
    # M3 - Deduplication
    # -------------------------

    deduplication = DeduplicationEngine(
        similarity_threshold=0.80
    )

    for result in reachable_results:

        duplicate = deduplication.check_duplicate(
            result.url,
            result.content_hash
        )

        assert duplicate is None

    assert deduplication.count_unique() >= 1

    # -------------------------
    # M4 - Liveness
    # -------------------------

    checker = LivenessChecker(
        timeout=20
    )

    liveness_result = checker.check(
        reachable_results[0].url
    )

    assert liveness_result.is_active is True
    assert liveness_result.status_code == 200

    # -------------------------
    # M6 - Storage
    # -------------------------

    store = DataStore("test_pipeline.db")

    record = ServiceRecord(
        url=reachable_results[0].url,
        first_seen_at=reachable_results[0].fetched_at,
        last_checked_at=liveness_result.last_checked_at,
        is_active=liveness_result.is_active,
        content_hash=reachable_results[0].content_hash,
        source="authorized-target"
    )

    store.add_service(record)

    assert store.count_services() >= 1

    store.close()
