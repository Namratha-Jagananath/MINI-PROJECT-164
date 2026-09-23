"""
Cloud Orchestration Module (M5)

Responsibility:
    Manage crawler workers and automatically calculate the
    required number of workers based on crawl workload.

This implementation provides:
    - Configurable minimum and maximum workers
    - Queue-depth based scaling
    - Multiple Tor crawler workers
    - Local orchestration for testing
"""

from dataclasses import dataclass
from math import ceil
from typing import List

from crawler import CrawlerPool, TorCrawlWorker, CrawlResult


@dataclass
class WorkerPoolConfig:
    """Configuration for crawler worker scaling."""

    min_workers: int = 1
    max_workers: int = 10
    target_queue_depth_per_worker: int = 50

    def __post_init__(self):
        if self.min_workers < 1:
            raise ValueError("min_workers must be at least 1")

        if self.max_workers < self.min_workers:
            raise ValueError("max_workers must be >= min_workers")

        if self.target_queue_depth_per_worker < 1:
            raise ValueError(
                "target_queue_depth_per_worker must be at least 1"
            )


class Orchestrator:
    """
    Local orchestration controller for the Tor crawler.

    Worker count is calculated from the current queue depth.
    """

    def __init__(self, config: WorkerPoolConfig | None = None):
        self.config = config or WorkerPoolConfig()
        self._queue_depth = 0
        self._current_workers = self.config.min_workers

    def set_queue_depth(self, queue_depth: int):
        """Set the number of pending crawl tasks."""

        if queue_depth < 0:
            raise ValueError("queue_depth cannot be negative")

        self._queue_depth = queue_depth

    def current_queue_depth(self) -> int:
        """Return the current queue depth."""

        return self._queue_depth

    def calculate_desired_workers(
        self,
        queue_depth: int | None = None
    ) -> int:
        """Calculate the required number of crawler workers."""

        if queue_depth is None:
            queue_depth = self.current_queue_depth()

        if queue_depth < 0:
            raise ValueError("queue_depth cannot be negative")

        if queue_depth == 0:
            return self.config.min_workers

        desired_workers = ceil(
            queue_depth /
            self.config.target_queue_depth_per_worker
        )

        return max(
            self.config.min_workers,
            min(
                desired_workers,
                self.config.max_workers
            )
        )

    def scale(self) -> int:
        """
        Calculate and apply the desired worker count.

        In this local implementation, applying the scaling
        decision means updating the internal worker count.
        """

        desired_workers = self.calculate_desired_workers()

        self._current_workers = desired_workers

        return self._current_workers

    def current_workers(self) -> int:
        """Return the current worker count."""

        return self._current_workers

    def create_workers(self) -> List[TorCrawlWorker]:
        """
        Create the required number of Tor crawler workers.
        """

        workers = []

        for worker_id in range(1, self._current_workers + 1):
            worker = TorCrawlWorker(
                worker_id=worker_id,
                timeout=10,
                max_retries=1
            )

            workers.append(worker)

        return workers

    def crawl(self, urls: List[str]) -> List[CrawlResult]:
        """
        Crawl authorized URLs using the orchestrated worker pool.
        """

        if not urls:
            return []

        self.set_queue_depth(len(urls))

        worker_count = self.scale()

        print("Orchestrator worker count:", worker_count)

        workers = self.create_workers()

        pool = CrawlerPool(workers)

        return pool.run(urls)


if __name__ == "__main__":

    print("========================================")
    print("        M5 ORCHESTRATION MODULE")
    print("========================================")

    config = WorkerPoolConfig(
        min_workers=1,
        max_workers=5,
        target_queue_depth_per_worker=2
    )

    orchestrator = Orchestrator(config)

    print("\nScaling demonstration")
    print("----------------------------")

    test_queue_sizes = [0, 1, 2, 3, 5, 10, 20]

    for queue_depth in test_queue_sizes:

        orchestrator.set_queue_depth(queue_depth)

        workers = orchestrator.scale()

        print(
            "Queue depth:",
            queue_depth,
            "-> Workers:",
            workers
        )

    print("\n========================================")
    print("      M5 ORCHESTRATION TEST COMPLETE")
    print("========================================")
