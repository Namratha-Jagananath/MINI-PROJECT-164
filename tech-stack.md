# Tech Stack & Feasibility

## Software / Technologies

- **Programming Language:** Python 3
- **Anonymity Layer:** Tor client (`stem` / `PySocks`) for .onion access
- **Crawling Framework:** Scrapy / custom asynchronous crawler
- **Machine Learning:** scikit-learn / PyTorch (similarity & mirror detection)
- **Containerization & Orchestration:** Docker, Kubernetes
- **Data Storage:** PostgreSQL / MongoDB
- **Cloud Platform:** AWS / GCP / Azure (elastic compute + storage)

## Hardware / Infrastructure Requirements

- Development machine: 8GB+ RAM, multi-core CPU for local testing
- Cloud compute instances: scalable VM/container instances for crawler worker nodes
- Cloud storage: for persisting enumerated URL datasets and logs

## Feasibility Study

**Technology Feasibility:** Built on mature, open-source technologies — Tor client libraries, Python crawling frameworks, standard ML libraries, container orchestration. No experimental or unavailable technology required.

**Cost Feasibility:** Free/open-source software throughout; cloud costs limited to compute instances for crawling and storage, starting small (single-node) and scaling only as needed.

**Resource Feasibility:** Deliverable scope is achievable within the academic project timeline by a team of 3, using freely available datasets/seed sources and standard lab/cloud-credit resources.

**Conclusion:** The proposed solution is technically achievable, cost-effective, and realistically scoped for the project timeline.
