from crawler import TorCrawlWorker, CrawlerPool

# Your own controlled .onion test service
host = (
    "lumz6w62s6jhdqpzbk35xlvcr25in7cgl3mjb5e5z5wi2u3x6me5w3yd"
    + ".onion"
)

url = "http://" + host

# Create two crawler workers
worker1 = TorCrawlWorker("worker-1")
worker2 = TorCrawlWorker("worker-2")

# Create the crawler pool
pool = CrawlerPool([worker1, worker2])

# Give two URLs to the pool
seed_urls = [url, url]

# Run the workers
results = pool.run(seed_urls)

# Display results
print("\n===== CRAWLER POOL RESULTS =====\n")

for result in results:
    print("URL:", result.url)
    print("Status:", result.status)
    print("Content Hash:", result.content_hash)
    print("Fetched At:", result.fetched_at)
    print("--------------------------------")
