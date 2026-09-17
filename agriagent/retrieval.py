from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from importlib.resources import files

from .language import normalize_text
from .types import Language

TOKEN_RE = re.compile(r"[\w\u0900-\u097F]+", re.UNICODE)


@dataclass(frozen=True)
class KnowledgeRecord:
    id: str
    crop: str
    topic: str
    source_group: str
    source_title: str
    source_url: str
    text_en: str
    text_ne: str
    text_roman: str
    tags: tuple[str, ...]

    def searchable_text(self) -> str:
        return " ".join(
            [self.crop, self.topic, self.text_en, self.text_ne, self.text_roman, *self.tags]
        )

    def localized_text(self, language: Language) -> str:
        if language == Language.NEPALI:
            return self.text_ne
        if language == Language.ROMANIZED_NEPALI:
            return self.text_roman
        return self.text_en


@dataclass(frozen=True)
class SearchHit:
    record: KnowledgeRecord
    score: float


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(normalize_text(text))


class LexicalRetriever:
    """Small BM25 retriever with deterministic source-quota merging."""

    def __init__(self, records: list[KnowledgeRecord], k1: float = 1.5, b: float = 0.75):
        self.records = records
        self.k1 = k1
        self.b = b
        self.doc_tokens = [tokenize(r.searchable_text()) for r in records]
        self.doc_freq: Counter[str] = Counter()
        for tokens in self.doc_tokens:
            self.doc_freq.update(set(tokens))
        self.avgdl = sum(map(len, self.doc_tokens)) / max(1, len(self.doc_tokens))

    @classmethod
    def from_package_data(cls) -> "LexicalRetriever":
        path = files("agriagent.data").joinpath("knowledge.json")
        raw = json.loads(path.read_text(encoding="utf-8"))
        records = [
            KnowledgeRecord(
                id=row["id"], crop=row["crop"], topic=row["topic"],
                source_group=row["source_group"], source_title=row["source_title"],
                source_url=row["source_url"], text_en=row["text_en"], text_ne=row["text_ne"],
                text_roman=row["text_roman"], tags=tuple(row.get("tags", [])),
            )
            for row in raw
        ]
        return cls(records)

    def _bm25(self, query: str) -> list[SearchHit]:
        q_tokens = tokenize(query)
        n_docs = len(self.records)
        hits: list[SearchHit] = []
        for idx, tokens in enumerate(self.doc_tokens):
            tf = Counter(tokens)
            dl = len(tokens)
            score = 0.0
            for term in q_tokens:
                df = self.doc_freq.get(term, 0)
                if not df:
                    continue
                idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
                freq = tf.get(term, 0)
                denom = freq + self.k1 * (1 - self.b + self.b * dl / max(self.avgdl, 1e-9))
                score += idf * (freq * (self.k1 + 1)) / denom if denom else 0.0
            if score > 0:
                hits.append(SearchHit(self.records[idx], score))
        return sorted(hits, key=lambda h: (-h.score, h.record.id))

    def search(
        self,
        query: str,
        *,
        top_k: int = 3,
        quotas: dict[str, int] | None = None,
        min_relative_score: float = 0.55,
    ) -> list[SearchHit]:
        ranked = self._bm25(query)
        if not ranked:
            return []

        # Never let source-diversity quotas force obviously weak matches into the answer.
        floor = ranked[0].score * min_relative_score
        ranked = [hit for hit in ranked if hit.score >= floor]
        quotas = quotas or {"government": 1, "university": 1, "extension": 1}
        selected: list[SearchHit] = []
        grouped: dict[str, list[SearchHit]] = defaultdict(list)
        for hit in ranked:
            grouped[hit.record.source_group].append(hit)

        # Quota pass: preserve source diversity.
        for group, quota in quotas.items():
            selected.extend(grouped.get(group, [])[:quota])

        # Score pass: fill remaining slots globally without duplicates.
        selected_ids = {h.record.id for h in selected}
        for hit in ranked:
            if len(selected) >= top_k:
                break
            if hit.record.id not in selected_ids:
                selected.append(hit)
                selected_ids.add(hit.record.id)

        return sorted(selected[:top_k], key=lambda h: (-h.score, h.record.id))
