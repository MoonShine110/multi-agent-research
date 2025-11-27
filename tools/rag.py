"""
RAG (Retrieval Augmented Generation) Module

This module provides vector storage for caching and retrieving past research.
Uses ChromaDB as the vector store.

WHY RAG?
- Avoids redundant web searches for similar queries
- Builds a knowledge base over time
- Enables semantic search across past findings
"""

import os
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings


class ResearchRAG:
    """
    RAG system for caching and retrieving research findings.
    
    Uses ChromaDB to store embeddings of research findings,
    allowing semantic similarity search for related past research.
    """
    
    def __init__(self, persist_directory: str = "./research_cache"):
        """
        Initialize the RAG system.
        
        Args:
            persist_directory: Directory to persist the vector store
        """
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Create or get the collection for research findings
        self.collection = self.client.get_or_create_collection(
            name="research_findings",
            metadata={"description": "Cached research findings for RAG"}
        )
    
    def add_findings(self, query: str, findings: List[Dict]) -> None:
        """
        Add research findings to the vector store.
        
        Args:
            query: The original research query
            findings: List of research findings to store
        """
        if not findings:
            return
        
        documents = []
        metadatas = []
        ids = []
        
        for i, finding in enumerate(findings):
            # Create a document from the finding
            doc_text = f"""
            Query: {query}
            Title: {finding.get('title', 'Unknown')}
            Content: {finding.get('content', '')}
            Source: {finding.get('source', 'Unknown')}
            """
            
            documents.append(doc_text)
            metadatas.append({
                "query": query,
                "source": finding.get("source", ""),
                "title": finding.get("title", "")
            })
            ids.append(f"{hash(query)}_{i}")
        
        # Add to collection (ChromaDB handles embeddings automatically)
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"   💾 Cached {len(findings)} findings to RAG store")
        except Exception as e:
            # Handle duplicate IDs gracefully
            print(f"   ⚠️ RAG cache update skipped: {e}")
    
    def search_similar(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Search for similar past research findings.
        
        Args:
            query: The search query
            n_results: Number of results to return
            
        Returns:
            List of similar findings from past research
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            if not results or not results['documents']:
                return []
            
            similar_findings = []
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                similar_findings.append({
                    "content": doc,
                    "source": metadata.get("source", ""),
                    "title": metadata.get("title", ""),
                    "original_query": metadata.get("query", "")
                })
            
            return similar_findings
            
        except Exception as e:
            print(f"   ⚠️ RAG search error: {e}")
            return []
    
    def has_similar_research(self, query: str, threshold: int = 3) -> bool:
        """
        Check if we have sufficient similar research cached.
        
        Args:
            query: The research query
            threshold: Minimum number of similar findings needed
            
        Returns:
            True if we have enough cached research
        """
        similar = self.search_similar(query, n_results=threshold)
        return len(similar) >= threshold
    
    def get_stats(self) -> Dict:
        """Get statistics about the RAG store."""
        return {
            "total_documents": self.collection.count(),
            "persist_directory": self.persist_directory
        }


# Simple in-memory fallback if ChromaDB has issues
class SimpleRAG:
    """
    Simple in-memory RAG fallback using keyword matching.
    Used if ChromaDB is not available.
    """
    
    def __init__(self):
        self.cache = {}  # query -> findings
    
    def add_findings(self, query: str, findings: List[Dict]) -> None:
        """Cache findings by query."""
        self.cache[query.lower()] = findings
        print(f"   💾 Cached {len(findings)} findings (in-memory)")
    
    def search_similar(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search by keyword overlap."""
        query_words = set(query.lower().split())
        results = []
        
        for cached_query, findings in self.cache.items():
            cached_words = set(cached_query.split())
            overlap = len(query_words & cached_words)
            if overlap > 0:
                for finding in findings[:n_results]:
                    finding['original_query'] = cached_query
                    results.append(finding)
        
        return results[:n_results]
    
    def has_similar_research(self, query: str, threshold: int = 3) -> bool:
        return len(self.search_similar(query)) >= threshold
    
    def get_stats(self) -> Dict:
        return {"total_queries": len(self.cache), "type": "in-memory"}


def create_rag(use_persistent: bool = True) -> object:
    """
    Factory function to create the appropriate RAG system.
    
    Args:
        use_persistent: Whether to use persistent ChromaDB storage
        
    Returns:
        RAG instance (ResearchRAG or SimpleRAG)
    """
    if use_persistent:
        try:
            return ResearchRAG()
        except Exception as e:
            print(f"⚠️ ChromaDB not available, using simple RAG: {e}")
            return SimpleRAG()
    return SimpleRAG()
