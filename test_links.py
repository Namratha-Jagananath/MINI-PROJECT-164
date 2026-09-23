from crawler import TorCrawlWorker

worker = TorCrawlWorker("test")

html = """
<html>
<body>
<a href="http://lumz6w62s6jhdqpzbk35xlvcr25in7cgl3mjb5e5z5wi2u3x6me5w3yd.onion">
Test Onion
</a>
</body>
</html>
"""

links = worker.extract_links(html)

print("Extracted links:")
for link in links:
    print(link)
