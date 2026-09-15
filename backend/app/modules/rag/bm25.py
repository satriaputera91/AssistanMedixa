import math
import re
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter


class BM25Engine:
    """
    High-Performance Okapi BM25 / BM25+ Ranking Engine.
    Provides term-frequency saturation, document length normalization,
    and inverse document frequency (IDF) calculation for clinical knowledge retrieval.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75, delta: float = 0.5):
        self.k1 = k1
        self.b = b
        self.delta = delta  # BM25+ lower bound enhancement
        self.doc_ids: List[str] = []
        self.doc_payloads: Dict[str, Dict[str, Any]] = {}
        self.doc_tokens: Dict[str, List[str]] = {}
        self.doc_lengths: Dict[str, int] = {}
        self.avg_doc_length: float = 0.0
        self.doc_freqs: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.total_docs: int = 0

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tokenize text into lowercase alphanumeric tokens with medical term preservation."""
        if not text:
            return []
        text = text.lower()
        # Keep words, digits, and hyphenated terms (e.g. icd-10, post-pci, hba1c)
        tokens = re.findall(r'[a-zA-Z0-9_-]+', text)
        return [t for t in tokens if len(t) > 1]

    def clear(self):
        """Clears all indexed document structures."""
        self.doc_ids = []
        self.doc_payloads = {}
        self.doc_tokens = {}
        self.doc_lengths = {}
        self.avg_doc_length = 0.0
        self.doc_freqs = {}
        self.idf = {}
        self.total_docs = 0

    def index_chunks(self, chunks: List[Dict[str, Any]]):
        """Builds / rebuilds BM25 index from a list of knowledge chunks."""
        self.clear()
        self.total_docs = len(chunks)
        if self.total_docs == 0:
            return

        total_len = 0
        df_counter: Counter = Counter()

        for chunk in chunks:
            chunk_id = chunk.get("chunk_id") or str(chunk.get("id"))
            self.doc_ids.append(chunk_id)
            self.doc_payloads[chunk_id] = chunk

            # Build enriched searchable document string
            searchable_parts = [
                chunk.get("title", ""),
                chunk.get("category", ""),
                chunk.get("specialty", ""),
                chunk.get("icd10_code", "") or "",
                chunk.get("rxnorm_code", "") or "",
                " ".join(chunk.get("synonyms", []) if isinstance(chunk.get("synonyms"), list) else []),
                " ".join(chunk.get("keywords", []) if isinstance(chunk.get("keywords"), list) else []),
                chunk.get("chunk_text", "") or chunk.get("content", "")
            ]
            doc_str = " ".join(filter(None, searchable_parts))
            tokens = self.tokenize(doc_str)

            self.doc_tokens[chunk_id] = tokens
            doc_len = len(tokens)
            self.doc_lengths[chunk_id] = doc_len
            total_len += doc_len

            # Update document frequency for unique tokens in this chunk
            unique_tokens = set(tokens)
            for t in unique_tokens:
                df_counter[t] += 1

        self.avg_doc_length = total_len / max(self.total_docs, 1)
        self.doc_freqs = dict(df_counter)

        # Compute Robertson-Spärck Jones IDF with smoothing
        for term, df in self.doc_freqs.items():
            # Standard BM25 IDF: ln((N - n + 0.5) / (n + 0.5) + 1.0)
            self.idf[term] = math.log(1.0 + (self.total_docs - df + 0.5) / (df + 0.5))

    def get_scores(self, query: str) -> Dict[str, float]:
        """Calculates raw BM25 scores for all indexed documents against a query."""
        if not query or self.total_docs == 0:
            return {}

        q_tokens = self.tokenize(query)
        if not q_tokens:
            return {}

        scores: Dict[str, float] = {}

        for doc_id, tokens in self.doc_tokens.items():
            doc_len = self.doc_lengths.get(doc_id, 1)
            tf_counter = Counter(tokens)
            score = 0.0

            # Length normalization factor
            len_norm = 1.0 - self.b + self.b * (doc_len / max(self.avg_doc_length, 1.0))

            for q_term in q_tokens:
                if q_term not in self.idf:
                    continue
                tf = tf_counter.get(q_term, 0)
                if tf > 0:
                    idf = self.idf[q_term]
                    # BM25 term score with BM25+ delta
                    term_score = idf * (((tf * (self.k1 + 1.0)) / (tf + self.k1 * len_norm)) + self.delta)
                    score += term_score

            scores[doc_id] = score

        return scores

    def get_normalized_scores(self, query: str) -> Dict[str, float]:
        """
        Calculates BM25 scores normalized to [0.0, 1.0] range
        using smooth saturation: raw_score / (raw_score + 6.0).
        """
        raw_scores = self.get_scores(query)
        normalized: Dict[str, float] = {}
        for doc_id, raw_val in raw_scores.items():
            if raw_val <= 0:
                normalized[doc_id] = 0.0
            else:
                # Soft saturation function mapping raw BM25 score smoothly to (0, 1)
                normalized[doc_id] = round(raw_val / (raw_val + 6.0), 4)
        return normalized

    def search(self, query: str, top_k: int = 20) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Returns top_k (chunk_id, normalized_score, payload) sorted by BM25 score."""
        norm_scores = self.get_normalized_scores(query)
        ranked = sorted(norm_scores.items(), key=lambda x: x[1], reverse=True)
        results = []
        for doc_id, score in ranked[:top_k]:
            if score > 0:
                results.append((doc_id, score, self.doc_payloads.get(doc_id, {})))
        return results
