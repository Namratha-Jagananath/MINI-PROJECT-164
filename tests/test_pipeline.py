import os
import tempfile

from seed_acquisition import SeedAcquisitionManager
from deduplication import DeduplicationEngine
from orchestration import WorkerPoolConfig, Orchestrator
from liveness_check import LivenessChecker
from storage import DataStore, ServiceRecord


CONTROLLED_ONION = (
    "http://lumz6w62s6jhdqpzbk35xlvcr25in7cgl3mjb5e5z5wi2u3x6me5w3yd.onion"
)


# ============================================================
# M1 - SEED ACQUISITION
# ============================================================

def test_valid_onion_url():
    manager = SeedAcquisitionManager()

    assert manager.is_valid_onion_url(
        CONTROLLED_ONION
    )


def test_invalid_onion_url():
    manager = SeedAcquisitionManager()

    assert not manager.is_valid_onion_url(
        "https://example.com"
    )


def test_seed_duplicate_removal():
    manager = SeedAcquisitionManager()

    first = manager.add_seed(
        CONTROLLED_ONION,
        "test"
    )

    second = manager.add_seed(
        CONTROLLED_ONION,
        "test"
    )

    assert first is True
    assert second is False
    assert len(manager.seeds) == 1


# ============================================================
# M3 - DEDUPLICATION
# ============================================================

def test_exact_duplicate_detection():
    engine = DeduplicationEngine()

    url1 = CONTROLLED_ONION + "/page1.html"
    url2 = CONTROLLED_ONION + "/page2.html"

    content = "same research content"

    result1 = engine.check_duplicate(
        url1,
        content
    )

    result2 = engine.check_duplicate(
        url2,
        content
    )

    assert result1 is None
    assert result2 is not None


def test_near_duplicate_detection():
    engine = DeduplicationEngine()

    url1 = CONTROLLED_ONION + "/page1.html"
    url2 = CONTROLLED_ONION + "/page2.html"

    content1 = (
        "Authorized Research Portal "
        "This page is used for controlled Tor crawler research. "
        "The system collects content for duplicate detection testing."
    )

    content2 = (
        "Authorized Research Portal "
        "This page is used for controlled Tor crawler research. "
        "The system collects content for duplicate detection testing. "
        "This is a slightly modified version for near-duplicate testing."
    )

    first = engine.check_similarity(
        url1,
        content1
    )

    second = engine.check_similarity(
        url2,
        content2
    )

    assert first is None
    assert second is not None
    assert second.similarity_score >= 0.8


# ============================================================
# M4 - LIVENESS
# ============================================================

def test_liveness_checker_initialization():
    checker = LivenessChecker()

    assert checker is not None


# ============================================================
# M5 - ORCHESTRATION
# ============================================================

def test_worker_scaling():
    config = WorkerPoolConfig(
        min_workers=1,
        max_workers=10,
        target_queue_depth_per_worker=1
    )

    orchestrator = Orchestrator(
        config
    )

    orchestrator.set_queue_depth(1)

    assert orchestrator.calculate_desired_workers() == 1

    orchestrator.set_queue_depth(3)

    assert orchestrator.calculate_desired_workers() == 3


def test_worker_limit():
    config = WorkerPoolConfig(
        min_workers=1,
        max_workers=10,
        target_queue_depth_per_worker=1
    )

    orchestrator = Orchestrator(
        config
    )

    orchestrator.set_queue_depth(100)

    assert orchestrator.calculate_desired_workers() == 10


# ============================================================
# M6 - SQLITE STORAGE
# ============================================================

def test_sqlite_storage():
    with tempfile.TemporaryDirectory() as temp_dir:

        database_path = os.path.join(
            temp_dir,
            "test.db"
        )

        datastore = DataStore(
            database_path
        )

        record = ServiceRecord(
            url=CONTROLLED_ONION + "/",
            first_seen_at="2026-01-01T00:00:00+00:00",
            last_checked_at="2026-01-01T00:01:00+00:00",
            is_active=True,
            content_hash="test_hash"
        )

        datastore.add_service(record)

        records = datastore.get_all_services()

        assert len(records) == 1
        assert records[0][0] == CONTROLLED_ONION + "/"
        assert records[0][3] == 1
        assert records[0][4] == "test_hash"

        assert datastore.count_services() == 1

        datastore.close()


# ============================================================
# CORE MODULE IMPORT TEST
# ============================================================

def test_core_modules_import():
    import crawler
    import liveness_check
    import orchestration
    import storage
    import deduplication
    import seed_acquisition

    assert crawler is not None
    assert liveness_check is not None
    assert orchestration is not None
    assert storage is not None
    assert deduplication is not None
    assert seed_acquisition is not None
