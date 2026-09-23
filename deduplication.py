from dataclasses import dataclass
from typing import Dict, List, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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

    def __init__(self, similarity_threshold: float = 0.80):

        self.similarity_threshold = similarity_threshold

        self.hash_to_url: Dict[str, str] = {}
        self.text_pages: Dict[str, str] = {}

        self.duplicates: List[DuplicateRecord] = []
        self.similar_pages: List[SimilarityRecord] = []

    def check_duplicate(
        self,
        url: str,
        content_hash: str
    ) -> Optional[DuplicateRecord]:

        if not content_hash:
            return None

        if content_hash in self.hash_to_url:

            original_url = self.hash_to_url[content_hash]

            record = DuplicateRecord(
                url=url,
                duplicate_of=original_url,
                content_hash=content_hash
            )

            self.duplicates.append(record)

            return record

        self.hash_to_url[content_hash] = url

        return None

    @staticmethod
    def normalize_text(text: str) -> str:

        if not text:
            return ""

        text = text.lower()

        cleaned = []

        for character in text:

            if character.isalnum() or character.isspace():
                cleaned.append(character)

        return " ".join(
            "".join(cleaned).split()
        )

    def check_similarity(
        self,
        url: str,
        text: str
    ) -> Optional[SimilarityRecord]:

        normalized_text = self.normalize_text(text)

        if not normalized_text:
            return None

        if not self.text_pages:

            self.text_pages[url] = normalized_text

            return None

        existing_urls = list(
            self.text_pages.keys()
        )

        existing_texts = list(
            self.text_pages.values()
        )

        documents = existing_texts + [
            normalized_text
        ]

        try:

            vectorizer = TfidfVectorizer(
                stop_words="english"
            )

            matrix = vectorizer.fit_transform(
                documents
            )

            new_vector = matrix[-1]
            old_vectors = matrix[:-1]

            scores = cosine_similarity(
                new_vector,
                old_vectors
            )[0]

        except ValueError:

            self.text_pages[url] = normalized_text

            return None

        best_match = None
        best_score = 0.0

        for index, score in enumerate(scores):

            score = float(score)

            if score > best_score:

                best_score = score
                best_match = existing_urls[index]

            if score >= self.similarity_threshold:

                record = SimilarityRecord(
                    url=url,
                    similar_to=existing_urls[index],
                    similarity_score=score
                )

                self.similar_pages.append(record)

        self.text_pages[url] = normalized_text

        if (
            best_match is not None
            and best_score >= self.similarity_threshold
        ):

            return SimilarityRecord(
                url=url,
                similar_to=best_match,
                similarity_score=best_score
            )

        return None

    def get_duplicates(
        self
    ) -> List[DuplicateRecord]:

        return self.duplicates

    def get_similar_pages(
        self
    ) -> List[SimilarityRecord]:

        return self.similar_pages

    def count_unique(self) -> int:

        return len(self.hash_to_url)

    def count_duplicates(self) -> int:

        return len(self.duplicates)

    def count_similar_pages(self) -> int:

        return len(self.similar_pages)


if __name__ == "__main__":

    print("=" * 60)
    print("TOR ML DEDUPLICATION MODULE")
    print("=" * 60)

    engine = DeduplicationEngine(
        similarity_threshold=0.80
    )

    print("\n[1] EXACT DUPLICATE TEST")

    engine.check_duplicate(
        "http://site1.onion",
        "hash_abc"
    )

    duplicate = engine.check_duplicate(
        "http://site2.onion",
        "hash_abc"
    )

    if duplicate:

        print("Exact duplicate detected")
        print("URL:", duplicate.url)
        print("Original:", duplicate.duplicate_of)
        print("Hash:", duplicate.content_hash)

    print("\n[2] TF-IDF + COSINE SIMILARITY TEST")

    page1 = """
    secure technology marketplace
    encrypted communication services
    privacy focused technology platform
    """

    page2 = """
    secure technology marketplace
    encrypted communication services
    privacy focused technology platform
    """

    page3 = """
    secure technology marketplace
    encrypted communication services
    privacy focused technology platform
    customer support technology information
    """

    engine.check_similarity(
        "http://site1.onion",
        page1
    )

    similarity = engine.check_similarity(
        "http://site3.onion",
        page2
    )

    if similarity:

        print("ML similarity match detected")
        print("URL:", similarity.url)
        print("Similar to:", similarity.similar_to)
        print(
            "Cosine similarity:",
            round(
                similarity.similarity_score,
                4
            )
        )

    similarity = engine.check_similarity(
        "http://site4.onion",
        page3
    )

    if similarity:

        print("ML similarity match detected")
        print("URL:", similarity.url)
        print("Similar to:", similarity.similar_to)
        print(
            "Cosine similarity:",
            round(
                similarity.similarity_score,
                4
            )
        )

    print("\n" + "=" * 60)
    print("ML DEDUPLICATION SUMMARY")
    print("=" * 60)

    print(
        "Unique content hashes:",
        engine.count_unique()
    )

    print(
        "Exact duplicates:",
        engine.count_duplicates()
    )

    print(
        "Near-duplicate matches:",
        engine.count_similar_pages()
    )

    print(
        "TF-IDF threshold:",
        engine.similarity_threshold
    )

    print("=" * 60)
