"""
Enhanced Agent Memory/Context Management with Optimization

This module provides optimized memory management with:
- Short-term (session-based) memory with size limits
- Long-term (ChromaDB vector DB) persistent memory
- Memory cleanup and optimization
- Metrics tracking for memory usage
"""

import logging
from typing import List, Tuple, Dict, Optional, Any
from datetime import datetime
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class MemoryMetrics:
    """Track memory usage metrics"""
    def __init__(self):
        self.short_term_count = 0
        self.long_term_count = 0
        self.cleanup_count = 0
        self.creation_time = datetime.now()

class AgentMemory:
    """
    Unified memory interface supporting both short-term (session) and long-term (vector DB) memory.
    - Short-term: in-memory list with size limits, cleared per session or on demand.
    - Long-term: persistent ChromaDB vector store with optimization.
    - Metrics: Track memory usage and performance
    """
    
    # Configuration
    MAX_SHORT_TERM_ITEMS = 1000  # Prevent unbounded growth
    CLEANUP_THRESHOLD = 0.8  # Cleanup when 80% full

    def __init__(self, collection_name: str = "agent_memory", max_short_term: int = 1000):
        """
        Initialize AgentMemory with enhanced optimization
        
        Args:
            collection_name: Name of ChromaDB collection
            max_short_term: Maximum items in short-term memory
        """
        # Short-term memory: session-based, fast access, not persisted
        self.short_term: List[Tuple[List[float], str, Dict]] = []
        self.max_short_term = max_short_term
        
        # Long-term memory: persistent, vector search
        try:
            self.client = chromadb.Client(Settings(
                persist_directory=".chroma_db",
                anonymized_telemetry=False
            ))
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Better for semantic search
            )
            logger.info(f"✅ ChromaDB initialized with collection: {collection_name}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize ChromaDB: {e}")
            self.collection = None
        
        # Memory metrics
        self.metrics = MemoryMetrics()
        logger.info(f"AgentMemory initialized (max_short_term={max_short_term})")

    # --- Short-term memory methods (optimized) ---
    def add_short_term(self, embedding: List[float], text: str, metadata: Optional[Dict] = None):
        """
        Add to short-term (session) memory with automatic cleanup
        
        Args:
            embedding: Vector embedding
            text: Text content
            metadata: Associated metadata
        """
        if not metadata or not isinstance(metadata, dict) or len(metadata) == 0:
            metadata = {"source": "short_term", "timestamp": datetime.now().isoformat()}
        
        # Add metadata if missing
        if "timestamp" not in metadata:
            metadata["timestamp"] = datetime.now().isoformat()
        
        self.short_term.append((embedding, text, metadata))
        self.metrics.short_term_count += 1
        
        # Auto-cleanup if threshold exceeded
        if len(self.short_term) > int(self.max_short_term * self.CLEANUP_THRESHOLD):
            self._cleanup_short_term()

    def get_short_term(self, n: Optional[int] = None) -> List[Tuple[List[float], str, Dict]]:
        """Get recent items from short-term memory"""
        if n is None:
            n = min(10, len(self.short_term))
        return self.short_term[-n:]

    def search_short_term(self, query_text: str, max_results: int = 5) -> List[Tuple[str, Dict]]:
        """Search short-term memory by text similarity"""
        results = []
        query_lower = query_text.lower()
        
        for embedding, text, metadata in self.short_term[-max_results * 2:]:
            if query_lower in text.lower():
                results.append((text, metadata))
        
        return results[:max_results]

    def _cleanup_short_term(self):
        """Remove oldest items from short-term memory when full"""
        items_to_remove = int(self.max_short_term * 0.2)  # Remove oldest 20%
        self.short_term = self.short_term[items_to_remove:]
        self.metrics.cleanup_count += 1
        logger.info(f"✅ Short-term memory cleaned (removed {items_to_remove} oldest items)")

    def clear_short_term(self):
        """Clear all short-term memory"""
        self.short_term = []
        logger.info("Short-term memory cleared")

    # --- Long-term memory methods (ChromaDB) ---
    def add_long_term(self, embedding: List[float], text: str, metadata: Optional[Dict] = None):
        """Add to long-term (persistent) memory"""
        if not metadata or not isinstance(metadata, dict) or len(metadata) == 0:
            metadata = {"source": "long_term", "timestamp": datetime.now().isoformat()}
        
        if "timestamp" not in metadata:
            metadata["timestamp"] = datetime.now().isoformat()
        
        try:
            if self.collection is None:
                logger.warning("ChromaDB collection not available, skipping add_long_term")
                return
            
            # Create unique ID for embedding
            doc_id = f"doc_{self.metrics.long_term_count}_{int(datetime.now().timestamp() * 1000)}"
            
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata]
            )
            self.metrics.long_term_count += 1
            logger.debug(f"✅ Added to long-term memory: {doc_id}")
        except Exception as e:
            logger.error(f"❌ Failed to add to long-term memory: {e}")
        self.collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata],
            ids=[str(hash(text))]
        )

    def search_long_term(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[float, str]]:
        """Vector search in long-term memory."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return list(zip(results['distances'][0], results['documents'][0]))

    def delete_long_term(self, text: str):
        """Delete from long-term memory by text."""
        self.collection.delete(ids=[str(hash(text))])

# Example usage:
# memory = AgentMemory()
# memory.add_short_term([0.1, 0.2, 0.3], "Short-term context")
# print(memory.get_short_term())
# memory.clear_short_term()
# memory.add_long_term([0.1, 0.2, 0.3], "Long-term context")
# print(memory.search_long_term([0.1, 0.2, 0.3]))
# memory.delete_long_term("Long-term context")
