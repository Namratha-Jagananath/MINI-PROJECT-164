# Literature Survey

10 papers reviewed — IEEE / Scopus-indexed / arXiv sources, 2024–2026.

| # | Paper | Venue / Year | Focus |
|---|---|---|---|
| 1 | Snorkeling in Dark Waters (Mimir) | IEEE TIFS, 2025 | Forum-based seeding + mirror detection |
| 2 | CRATOR: A CRAwler for TOR | ESORICS, 2024 | CAPTCHA-aware crawling |
| 3 | Dizzy: Large-Scale Crawling of Onion Services | arXiv, 2024 | Distributed high-throughput crawling |
| 4 | A Big Data Architecture for Dark Web Site Identification | Future Gen. Comp. Sys., 2024 | Cloud-scale (Kubernetes/Kafka) discovery pipeline |
| 5 | ATOL / LIGHTS: Large-Scale Onion Topic Labeling | ACM SIGKDD | Automated classification of crawled onion sites |
| 6 | Deanonymization of Hidden Services Categorized on Tor Darknet | Springer, 2025 | Address compilation via darknet scraping + Shodan |
| 7 | Recognition of Tor Malware and Onion Services | 2024 | Seed extraction via malware sandboxing |
| 8 | DarkFusionNet | Springer KSEM, 2025/26 | Fusion neural network for darknet content classification |
| 9 | Open-World Darknet Traffic Recognition (Leave-One-Service-Out) | arXiv, Aug 2026 | Generalization failure of classifiers on unseen services |
| 10 | Intelligent DL Framework for Profiling Darknet Traffic (CNN+BiLSTM) | MDPI, Feb 2026 | Traffic-based darknet classification |

## Core Comparison

| Paper | Strength | Limitation | Our Project's Improvement |
|---|---|---|---|
| Mimir (TIFS 2025) | Forum-based seeding; mirror detection at scale | Heuristic, not learned, deduplication | ML-based similarity model for mirrors |
| CRATOR (ESORICS 2024) | Bypasses CAPTCHA/anti-bot defenses | Static seed list; coverage plateaus | Multi-channel, continuously refreshed seeds |
| Dizzy (arXiv) | High-throughput distributed crawling | Depends only on organically found links | Combines distributed crawling + active seeding |

## Existing Methods and Drawbacks (Remaining Papers)

| Paper | Existing Method | Drawback |
|---|---|---|
| Big Data Architecture (2024) | Kubernetes/Kafka/Kubeflow pipeline for near-real-time onion discovery + BERTopic classification | Modest throughput (~2,066 services/week) relative to heavy infra cost |
| ATOL / LIGHTS | Large-scale crawl (100M+ pages) + automated topic labeling | Focuses on classification after crawling, not on improving enumeration efficiency |
| Deanonymization of Hidden Services (2025) | Compiles addresses via darknet scraping + Shodan | Small-scale evaluation; scraping approach not detailed enough to be reproducible |
| Recognition of Tor Malware & Onion Services (2024) | Extracts onion URLs by sandboxing malware and mining logs | Narrow seed source — only surfaces addresses malware authors hardcode |
| DarkFusionNet | Fusion neural network for darknet text classification | Downstream classifier only — needs already-crawled content, doesn't discover new URLs |
| Open-World Darknet Traffic Recognition (2026) | Tests classifier generalization to unseen services | Accuracy drops sharply (e.g., 87%→46%) on services not seen in training |

## Overall Gap

Existing work optimizes only ONE stage of the pipeline (seeding, evasion, throughput, or classification) in isolation. No reviewed system unifies multi-channel seed discovery + anonymity-preserving crawling + ML-based deduplication + elastic scaling — which is the gap this project targets.

## Challenges Identified

- Getting sufficient network coverage from a limited, single-source seed list.
- Handling anti-bot/anti-crawling defenses without breaking anonymity guarantees.
- Detecting near-duplicate mirror sites accurately (heuristics are brittle to minor content changes).
- Scaling the crawling/verification pipeline cost-efficiently on cloud infrastructure.
- Constant churn of hidden services making static datasets stale quickly.
- Ensuring ethical, research-only use of enumeration for defensive/threat-intelligence purposes.
