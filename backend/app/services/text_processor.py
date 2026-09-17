import re
from typing import List


class TextProcessor:
    """
    Handles text sanitization and semantic chunking with overlap for
    DOM-extracted content, notes, and academic documents.
    """

    @staticmethod
    def clean_text(raw_text: str) -> str:
        """
        Sanitizes raw text extracted from DOM or documents by normalizing whitespace,
        removing non-printable characters, and standardizing line breaks.
        """
        if not raw_text:
            return ""

        # Normalize line endings
        text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

        # Collapse horizontal whitespace (tabs, spaces) to single space
        text = re.sub(r"[ \t]+", " ", text)

        # Collapse more than two consecutive newlines into double newlines (paragraphs)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    @classmethod
    def chunk_text(
        cls,
        text: str,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
    ) -> List[str]:
        """
        Splits text into semantically coherent chunks using a hierarchical recursive strategy
        (paragraphs -> sentences -> clauses -> words) while preserving context with overlap.

        Args:
            text: Input clean text.
            chunk_size: Maximum character length per chunk (approx. 150-200 words).
            chunk_overlap: Number of overlapping characters preserved from previous chunk.

        Returns:
            A list of chunk strings.
        """
        cleaned = cls.clean_text(text)
        if not cleaned:
            return []

        if len(cleaned) <= chunk_size:
            return [cleaned]

        separators = ["\n\n", "\n", ". ", "? ", "! ", "; ", ", ", " "]
        return cls._recursive_split(cleaned, separators, chunk_size, chunk_overlap)

    @classmethod
    def _recursive_split(
        cls,
        text: str,
        separators: List[str],
        chunk_size: int,
        chunk_overlap: int,
    ) -> List[str]:
        final_chunks: List[str] = []

        if not separators:
            # Base case: split arbitrarily if no separators left
            start = 0
            while start < len(text):
                end = start + chunk_size
                final_chunks.append(text[start:end].strip())
                start += chunk_size - chunk_overlap
            return [c for c in final_chunks if c]

        separator = separators[0]
        remaining_separators = separators[1:]

        if separator in text:
            splits = text.split(separator)
        else:
            return cls._recursive_split(text, remaining_separators, chunk_size, chunk_overlap)

        current_chunk: List[str] = []
        current_len = 0

        for segment in splits:
            seg_len = len(segment) + len(separator)

            if current_len + seg_len <= chunk_size:
                current_chunk.append(segment)
                current_len += seg_len
            else:
                if current_chunk:
                    joined = separator.join(current_chunk).strip()
                    if joined:
                        final_chunks.append(joined)

                    # Build overlap buffer from the tail of current_chunk
                    overlap_acc: List[str] = []
                    overlap_len = 0
                    for item in reversed(current_chunk):
                        if overlap_len + len(item) <= chunk_overlap:
                            overlap_acc.insert(0, item)
                            overlap_len += len(item) + len(separator)
                        else:
                            break
                    current_chunk = overlap_acc
                    current_len = overlap_len

                if len(segment) > chunk_size:
                    # Subdivide oversized segment using more granular separators
                    sub_chunks = cls._recursive_split(
                        segment, remaining_separators, chunk_size, chunk_overlap
                    )
                    final_chunks.extend(sub_chunks)
                    current_chunk = []
                    current_len = 0
                else:
                    current_chunk.append(segment)
                    current_len += seg_len

        if current_chunk:
            joined = separator.join(current_chunk).strip()
            if joined:
                final_chunks.append(joined)

        return [c for c in final_chunks if c]


# Global instance
text_processor = TextProcessor()
