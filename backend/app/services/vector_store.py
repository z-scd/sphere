"""
FAISS vector store service
File: services/vector_store.py
"""

import os
import pickle
import faiss
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer


class VectorStore:
    """Manages FAISS vector database for document embeddings"""

    def __init__(
        self, index_path: str, metadata_path: str, model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize vector store with embedding model

        Args:
            model_name: Name of the sentence transformer model
        """
        self.model_name = model_name
        self.embedding_model = SentenceTransformer(model_name)
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()

        # Initialize FAISS index (using L2 distance)
        self.index = faiss.IndexFlatL2(self.dimension)

        # Store document metadata
        self.documents = []

        # Paths for persistence

        self.index_path = index_path
        self.metadata_path = metadata_path

    def add_documents(self, chunks: List[Dict], silent: bool = False) -> None:
        """
        Add document chunks to the vector store

        Args:
            chunks: List of dictionaries with 'content' and 'metadata'
            silent: If True, suppress progress output
        """
        if not chunks:
            return

        # Extract text content
        texts = [chunk["content"] for chunk in chunks]

        # Generate embeddings
        embeddings = self.embedding_model.encode(
            texts, show_progress_bar=not silent, convert_to_numpy=True
        )

        # Add to FAISS index
        self.index.add(embeddings.astype("float32"))

        # Store metadata
        self.documents.extend(chunks)

        # Save to disk
        self.save_index()

        if not silent:
            print(f"✅ Added {len(chunks)} chunks to vector store")

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar documents

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of dictionaries with document content and metadata
        """
        if self.index.ntotal == 0:
            return []

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)

        # Search FAISS index
        distances, indices = self.index.search(
            query_embedding.astype("float32"), min(top_k, self.index.ntotal)
        )

        # Prepare results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                # Convert L2 distance to similarity score (inverse)
                # Lower distance = higher similarity
                similarity = 1 / (1 + distances[0][i])
                doc["similarity"] = similarity
                results.append(doc)

        return results

    def save_index(self) -> None:
        """Save FAISS index and metadata to disk"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, self.index_path)

            # Save metadata
            with open(self.metadata_path, "wb") as f:
                pickle.dump(self.documents, f)

            print(f"💾 Index saved with {self.index.ntotal} vectors")
        except Exception as e:
            print(f"⚠️ Error saving index: {str(e)}")

    def load_index(self) -> None:
        """Load FAISS index and metadata from disk"""
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
                # Load FAISS index
                self.index = faiss.read_index(self.index_path)

                # Load metadata
                with open(self.metadata_path, "rb") as f:
                    self.documents = pickle.load(f)

                print(
                    f"📂 Loaded index with {self.index.ntotal} vectors and {len(self.documents)} document chunks"
                )
            else:
                print("ℹ️ No existing index found, starting fresh")
        except Exception as e:
            print(f"⚠️ Error loading index: {str(e)}")
            # Reset to empty index if loading fails
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []

    def clear_index(self) -> None:
        """Clear the entire index and metadata"""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self.save_index()
        print("🗑️ Index cleared")

    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        return {
            "total_vectors": self.index.ntotal,
            "total_documents": len(self.documents),
            "dimension": self.dimension,
            "model": self.model_name,
        }
