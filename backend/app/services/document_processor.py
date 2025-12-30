"""
Document processing service
File: services/document_processor.py
"""

import os
from typing import List, Dict
import re
from PyPDF2 import PdfReader


class DocumentProcessor:
    """Handles document loading and chunking"""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize document processor

        Args:
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_document(self, file_path: str, filename: str) -> List[Dict]:
        """
        Process a document and return chunks with metadata

        Args:
            file_path: Path to the document
            filename: Original filename

        Returns:
            List of dictionaries containing text chunks and metadata
        """
        # Extract text based on file type
        file_ext = os.path.splitext(filename)[1].lower()

        if file_ext == ".pdf":
            text = self._extract_pdf(file_path)
        elif file_ext in [".txt", ".md"]:
            text = self._extract_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

        # Clean the text
        text = self._clean_text(text)

        # Create chunks
        chunks = self._create_chunks(text)

        # Add metadata
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            processed_chunks.append(
                {
                    "content": chunk,
                    "metadata": {
                        "source": filename,
                        "chunk_id": i,
                        "total_chunks": len(chunks),
                    },
                }
            )

        return processed_chunks

    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error extracting PDF: {str(e)}")

    def _extract_text(self, file_path: str) -> str:
        """Extract text from plain text file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Error reading text file: {str(e)}")

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove special characters but keep medical terms
        text = re.sub(r"[^\w\s\-.,;:()/]", "", text)
        return text.strip()

    def _create_chunks(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks

        Args:
            text: Input text to chunk

        Returns:
            List of text chunks
        """
        if not text:
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            # Calculate end position
            end = start + self.chunk_size

            # If this is not the last chunk, try to break at a sentence
            if end < text_length:
                # Look for sentence endings near the chunk boundary
                chunk_text = text[start:end]
                last_period = chunk_text.rfind(".")
                last_newline = chunk_text.rfind("\n")

                # Use the last sentence ending if found
                break_point = max(last_period, last_newline)
                if break_point > self.chunk_size * 0.5:  # Only if it's not too early
                    end = start + break_point + 1

            # Extract chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start position (with overlap)
            start = end - self.chunk_overlap

        return chunks
