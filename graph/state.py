"""
State Schema for Multi-Agent Research Assistant

This defines the shared state that flows between all agents in the graph.
Think of it as a "data contract" - every agent reads from and writes to this state.
"""

from typing import TypedDict, List, Optional
from typing_extensions import Annotated
from langgraph.graph.message import add_messages


class ResearchFinding(TypedDict):
    """A single research finding from web search."""
    source: str          # URL of the source
    title: str           # Title of the article/page
    content: str         # Extracted content/snippet
    relevance: str       # Why this is relevant to the query


class ResearchState(TypedDict):
    """
    The shared state that passes through the entire graph.
    
    Flow:
    1. User provides 'query'
    2. Research Agent fills 'search_queries', 'findings'
    3. Summary Agent fills 'executive_summary', 'key_insights'
    """
    
    # === INPUT ===
    query: str                              # Original user question/topic
    
    # === RESEARCH AGENT OUTPUTS ===
    search_queries: List[str]               # Generated search queries
    findings: List[ResearchFinding]         # Collected research findings
    sources_consulted: int                  # Number of sources checked
    research_complete: bool                 # Flag: is research done?
    
    # === SUMMARY AGENT OUTPUTS ===
    executive_summary: str                  # Final executive summary
    key_insights: List[str]                 # Bullet point insights
    
    # === METADATA ===
    messages: Annotated[list, add_messages] # Conversation history (for memory)
    iteration_count: int                    # How many research iterations
    error: Optional[str]                    # Any error messages
