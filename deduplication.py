"""
Deduplication Module (M3)

Detects:
1. Exact duplicates using content hashes
2. Similar pages using text similarity
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import re
from difflib import SequenceMatcher


@dataclass
class DuplicateRecord:
    url: str
    duplicate_of: str
    content_hash: str


@dataclass
class SimilarityRecord:
    url: str
    similar_to: str
    similarity_score: float


class DeduplicationEngine:
    """Detects exact duplicates and similar pages."""

    def __init__(self, similarity_threshold: float = 0.80):
        self.hash_to_url: Dict[str, str] = {}
        self.text_pages: Dict[str, str] = {}

        self.duplicates: List[DuplicateRecord] = []
        self.similar_pages: List[SimilarityRecord] = []

        self.similarity_threshold = similarity_threshold

    # --------------------------------------------------
    # EXACT DUPLICATE DETECTION
    # --------------------------------------------------

    def check_duplicate(
        self,
        url: str,
        content_hash: str
    ) -> Optional[DuplicateRecord]:

        if content_hash in self.hash_to_url:

            original_url = self.hash_to_url[content_hash]

            duplicate = DuplicateRecord(
                url=url,
                duplicate_of=original_url,
                content_hash=content_hash
            )

            self.duplicates.append(duplicate)

            return duplicate

        self.hash_to_url[content_hash] = url

        return None

    # --------------------------------------------------
    # TEXT NORMALIZATION
    # --------------------------------------------------

    def normalize_text(self, text: str) -> str:
        """
        Convert text to a normalized form before comparison.
        """

        text = text.lower()

        text = re.sub(r"\s+", " ", text)

        text = re.sub(r"[^a-z0-9 ]", "", text)

        return text.strip()

    # --------------------------------------------------
    # SIMILARITY DETECTION
    # --------------------------------------------------

    def check_similarity(
        self,
        url: str,
        text: str
    ) -> List[SimilarityRecord]:

        normalized_text = self.normalize_text(text)

        results = []

        for existing_url, existing_text in self.text_pages.items():

            score = SequenceMatcher(
                None,
                normalized_text,
                existing_text
            ).ratio()

            if score >= self.similarity_threshold:

                record = SimilarityRecord(
                    url=url,
                    similar_to=existing_url,
                    similarity_score=round(score, 3)
                )

                self.similar_pages.append(record)

                results.append(record)

        self.text_pages[url] = normalized_text

        return results

    # --------------------------------------------------
    # RESULTS
    # --------------------------------------------------

    def get_duplicates(self) -> List[DuplicateRecord]:

        return self.duplicates

    def get_similar_pages(self) -> List[SimilarityRecord]:

        return self.similar_pages

    def count_unique(self) -> int:

        return len(self.hash_to_url)

    def count_duplicates(self) -> int:

        return len(self.duplicates)

    def count_similar_pages(self) -> int:

        return len(self.similar_pages)


# ------------------------------------------------------
# DEMO / TEST
# ------------------------------------------------------

if __name__ == "__main__":

    engine = DeduplicationEngine(
        similarity_threshold=0.80
    )

    print("========================================")
    print("        TOR DEDUPLICATION MODULE")
    print("========================================")

    # Exact duplicate test

    engine.check_duplicate(
        "http://site1.onion",
        "hash_abc"
    )

    duplicate = engine.check_duplicate(
        "http://site2.onion",
        "hash_abc"
    )

    # Unique page

    engine.check_duplicate(
        "http://site3.onion",
        "hash_xyz"
    )

    # Similar page test

    text1 = """
    Welcome to our secure online service.
    Login to access your account.
    Contact support for assistance.
    """

    text2 = """
    Welcome to our secure online service.
    Login to access your account.
    Contact support for assistance.
    """

    text3 = """
    This is a completely different website.
    It provides unrelated information and services.
    """

    engine.check_similarity(
        "http://site1.onion",
        text1
    )

    similar = engine.check_similarity(
        "http://site4.onion",
        text2
    )

    engine.check_similarity(
        "http://site5.onion",
        text3
    )

    print()

    print("Unique pages:", engine.count_unique())

    print("Exact duplicates:", engine.count_duplicates())

    print("Similar pages:", engine.count_similar_pages())

    print()

    if duplicate:

        print("Exact duplicate detected:")
        print("URL:", duplicate.url)
        print("Original:", duplicate.duplicate_of)
        print("Hash:", duplicate.content_hash)

    print()

    for record in similar:

        print("Similar page detected:")
        print("URL:", record.url)
        print("Similar to:", record.similar_to)
        print("Similarity score:", record.similarity_score)
