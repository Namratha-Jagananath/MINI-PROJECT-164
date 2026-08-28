# Efficient Enumeration of URLs of Active Hidden Services over Anonymous Channel (TOR)

**Project Code:** RJ_164
**Domain:** Artificial Intelligence, Cloud Computing
**SDG Alignment:** SDG 9 — Industry, Innovation and Infrastructure
**Institution:** Presidency School of Computer Science and Engineering, Presidency University, Bengaluru

## Team

| Name | Roll Number |
|---|---|
| Namratha J | 20231CSE0410 |
| Srushti Manjunath Guggari | 20231CSE0414 |
| Aishwarya | 20231CSE0419 |

**Guide:** Shreya Singh, Assistant Professor

## Status

📋 **Review 1 — Design & Literature Survey stage.** This repo currently holds the project proposal, literature review, and architecture design. Implementation is in progress; module stubs are provided in `src/` as a scaffold for upcoming development sprints.

## Abstract

This project proposes a research pipeline for studying discovery and cataloguing of active Tor hidden services (.onion sites), aimed at strengthening digital-infrastructure security tooling for defensive and threat-intelligence purposes. The design combines multi-source seed acquisition, a distributed crawler, machine-learning-based duplicate/mirror detection, and a continuous liveness-check module, deployed on an elastic cloud pipeline. The goal is to improve network coverage and reduce redundant crawling for legitimate security-research use cases (e.g., academic dark-web monitoring, threat-intel research), consistent with the source literature reviewed below.

## Objectives

1. Design a multi-channel seed-acquisition module drawing from at least 3 independent sources (onion search engines, surface-web forums, threat-intel feeds).
2. Design a distributed crawler capable of concurrently traversing hidden-service links while preserving anonymity guarantees.
3. Develop an ML-based similarity/deduplication model to identify mirror/duplicate onion sites.
4. Deploy the pipeline on an elastic, containerized cloud architecture.
5. Implement a continuous liveness-verification module to keep the dataset current.
6. Evaluate on measurable outcomes: unique-service coverage per seed, redundant-crawl reduction, and throughput under scaling.

## Literature Survey

10 papers reviewed (IEEE / Scopus-indexed / arXiv, 2024–2026) covering forum-based seeding, CAPTCHA-aware crawling, distributed crawling, cloud-scale discovery pipelines, and darknet traffic classification. See `docs/literature-survey.md` for the full comparison table and per-paper gap analysis.

**Key gap identified:** existing work optimizes only one stage of the pipeline (seeding, evasion, throughput, or classification) in isolation — no reviewed system unifies multi-channel seeding + anonymity-preserving crawling + ML deduplication + elastic scaling.

## Proposed Architecture

```
Multi-Channel Seed Acquisition
        ↓
Distributed Crawler (Tor)
        ↓
ML-Based Deduplication
        ↓
Elastic Cloud Deployment
        ↓
Continuous Liveness Check
```

### Modules

| ID | Module | Responsibility |
|---|---|---|
| M1 | Seed Acquisition | Collects and normalizes candidate .onion addresses from multiple sources |
| M2 | Distributed Crawler | Traverses candidate addresses concurrently over Tor |
| M3 | Deduplication | ML similarity model to filter mirror/duplicate sites |
| M4 | Liveness Verification | Periodically re-checks which services are still active |
| M5 | Cloud Orchestration | Manages containerized deployment and worker-pool scaling |
| M6 | Storage & Reporting | Persists URLs/metadata and generates summary reports |

## Tech Stack (Planned)

- **Language:** Python 3
- **ML:** scikit-learn / PyTorch
- **Containerization:** Docker, Kubernetes
- **Storage:** PostgreSQL / MongoDB
- **Cloud:** AWS / GCP / Azure

See `docs/tech-stack.md` for the full hardware/software breakdown and feasibility study.

## Repository Structure

```
.
├── README.md
├── requirements.txt
├── docs/
│   ├── literature-survey.md
│   ├── tech-stack.md
│   └── timeline.md
├── presentations/
│   └── RJ_164_Review1_Presentation.pptx
└── src/
    ├── seed_acquisition.py
    ├── crawler.py
    ├── deduplication.py
    ├── liveness_check.py
    ├── orchestration.py
    └── storage.py
```

## Scope & Ethics Note

This project is scoped as **academic security research** (dark-web monitoring / threat intelligence for defensive purposes), per the objectives above and the SDG 9 framing. Any crawler implementation built from this scaffold should be operated only against services and in the manner permitted by the team's institutional/ethics guidelines, and should not be used to bypass access controls on systems the team does not have authorization to test.

## License

Add a license (e.g. MIT, Apache-2.0) once decided by the team.
