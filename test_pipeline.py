from seed_acquisition import SeedAcquisitionManager
from crawler import TorCrawlWorker, CrawlerPool


print("\n========================================")
print("       TOR HIDDEN SERVICE PIPELINE")
print("========================================\n")


# ----------------------------------------
# STEP 1: SEED ACQUISITION
# ----------------------------------------

print("[1] Seed Acquisition")

manager = SeedAcquisitionManager("seeds.txt")

seeds = manager.acquire_seeds()

print("Unique seeds found:", len(seeds))

for seed in seeds:
    print("Seed:", seed.url)


# ----------------------------------------
# STEP 2: PREPARE URLS FOR CRAWLER
# ----------------------------------------

seed_urls = [seed.url for seed in seeds]


# ----------------------------------------
# STEP 3: CREATE CRAWLER WORKERS
# ----------------------------------------

print("\n[2] Creating Crawler Pool")

worker1 = TorCrawlWorker("worker-1")
worker2 = TorCrawlWorker("worker-2")

pool = CrawlerPool([worker1, worker2])


# ----------------------------------------
# STEP 4: CRAWL SEEDS
# ----------------------------------------

print("\n[3] Crawling Seeds")

results = pool.run(seed_urls)


# ----------------------------------------
# STEP 5: DISPLAY RESULTS
# ----------------------------------------

print("\n[4] Crawl Results\n")

reachable = 0
failed = 0

for result in results:

    print("URL:", result.url)
    print("Status:", result.status)
    print("Content Hash:", result.content_hash)
    print("Fetched At:", result.fetched_at)
    print("----------------------------------------")

    if result.status == "reachable":
        reachable += 1
    else:
        failed += 1


# ----------------------------------------
# SUMMARY
# ----------------------------------------

print("\n========================================")
print("              SUMMARY")
print("========================================")

print("Seeds found:", len(seeds))
print("URLs crawled:", len(results))
print("Reachable:", reachable)
print("Failed:", failed)

print("========================================")
print("          PIPELINE COMPLETED")
print("========================================")
