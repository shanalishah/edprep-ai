"""
Lightweight retrieval service over local IELTS PDFs using TF-IDF.
Indexes PDF text into chunks and provides top-k search with source citations.
"""

from __future__ import annotations

import os
import json
from dataclasses import dataclass
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from pypdf import PdfReader  # type: ignore
except Exception:  # pragma: no cover
    PdfReader = None  # allow import without hard dependency during tests


@dataclass
class Chunk:
    text: str
    source: str  # file path
    page: int


class TfidfRetriever:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=50000)
        self._matrix = None
        self._chunks: List[Chunk] = []

    @staticmethod
    def _read_pdf_text(path: str) -> List[Tuple[int, str]]:
        if PdfReader is None:
            raise RuntimeError("pypdf not installed; please install to enable PDF indexing")
        reader = PdfReader(path)
        pages: List[Tuple[int, str]] = []
        for i, page in enumerate(reader.pages):
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
            pages.append((i + 1, text))
        return pages

    @staticmethod
    def _chunk(text: str, size: int, overlap: int) -> List[str]:
        tokens = text.split()
        chunks: List[str] = []
        i = 0
        while i < len(tokens):
            chunk_tokens = tokens[i:i + size]
            if not chunk_tokens:
                break
            chunks.append(" ".join(chunk_tokens))
            i += max(1, size - overlap)
        return chunks

    def index_pdfs(self, pdf_paths: List[str]):
        chunks: List[Chunk] = []
        for path in pdf_paths:
            if not os.path.exists(path):
                continue
            for page_num, text in self._read_pdf_text(path):
                if not text.strip():
                    continue
                for c in self._chunk(text, self.chunk_size, self.chunk_overlap):
                    chunks.append(Chunk(text=c, source=path, page=page_num))
        self._chunks = chunks
        corpus = [c.text for c in chunks]
        if corpus:
            self._matrix = self.vectorizer.fit_transform(corpus)

    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {
            "chunks": [{"text": c.text, "source": c.source, "page": c.page} for c in self._chunks],
            "vocabulary_": getattr(self.vectorizer, 'vocabulary_', None),
            "idf_": getattr(self.vectorizer, 'idf_', None).tolist() if getattr(self.vectorizer, 'idf_', None) is not None else None,
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f)

    def load(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self._chunks = [Chunk(**c) for c in data.get("chunks", [])]
        self.vectorizer.vocabulary_ = data.get("vocabulary_")
        idf = data.get("idf_")
        if idf is not None:
            import numpy as np  # local import to avoid global dependency
            self.vectorizer.idf_ = np.array(idf)
        # Rebuild matrix
        corpus = [c.text for c in self._chunks]
        if corpus and self.vectorizer.vocabulary_ is not None:
            self._matrix = self.vectorizer.transform(corpus)

    def search(self, query: str, k: int = 3) -> List[Chunk]:
        if not query or self._matrix is None or not self._chunks:
            return []
        q_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(q_vec, self._matrix).ravel()
        top_idx = scores.argsort()[::-1][:k]
        return [self._chunks[i] for i in top_idx]


