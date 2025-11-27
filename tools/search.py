"""
Web Search Tool for Research Agent

This module provides web search functionality using DuckDuckGo search.
We use DuckDuckGo because it's free and doesn't require an API key.
"""

import os
from typing import List, Dict

try:
    from ddgs import DDGS
except ImportError:
    # Fallback for older package name
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        print("❌ Please install search package: pip install ddgs")
        DDGS = None


def web_search(query: str, max_results: int = 5) -> List[Dict]:
    """
    Perform a web search and return results.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of dictionaries containing search results with keys:
        - title: Page title
        - link: URL
        - snippet: Brief description/excerpt
    """
    if DDGS is None:
        print("❌ Search not available. Install with: pip install ddgs")
        return []
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            
            # Normalize the results format
            normalized = []
            for r in results:
                normalized.append({
                    "title": r.get("title", ""),
                    "link": r.get("href", r.get("link", "")),
                    "snippet": r.get("body", r.get("snippet", ""))
                })
            
            return normalized
            
    except Exception as e:
        print(f"Search error: {e}")
        return []


def web_search_multiple(queries: List[str], max_results_per_query: int = 3) -> List[Dict]:
    """
    Perform multiple web searches and combine results.
    
    Args:
        queries: List of search query strings
        max_results_per_query: Maximum results per query
        
    Returns:
        Combined list of all search results (deduplicated by URL)
    """
    all_results = []
    seen_urls = set()
    
    for query in queries:
        results = web_search(query, max_results=max_results_per_query)
        
        for result in results:
            url = result.get("link", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                result["query"] = query  # Track which query found this
                all_results.append(result)
    
    return all_results


# LangChain Tool wrapper (for integration with LangGraph)
def create_search_tool():
    """Create a LangChain-compatible tool for web search."""
    from langchain_core.tools import tool
    
    @tool
    def search_web(query: str) -> str:
        """
        Search the web for information on a topic.
        
        Args:
            query: The search query
            
        Returns:
            Search results as formatted string
        """
        results = web_search(query, max_results=5)
        
        if not results:
            return "No results found."
        
        output = []
        for i, r in enumerate(results, 1):
            output.append(f"{i}. {r['title']}\n   URL: {r['link']}\n   {r['snippet']}\n")
        
        return "\n".join(output)
    
    return search_web
