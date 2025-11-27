"""
Guardrails and Safety Controls

This module provides input validation, content filtering, and safety controls
to ensure the research assistant operates safely and responsibly.
"""

import re
from typing import Tuple, List

# Topics that should be handled with extra care or refused
SENSITIVE_TOPICS = [
    "how to make weapons",
    "how to hack",
    "illegal drugs",
    "how to harm",
    "exploit vulnerabilities",
]

# Maximum limits to prevent abuse
MAX_QUERY_LENGTH = 500
MAX_SEARCH_QUERIES = 5
MAX_ITERATIONS = 3


def validate_input(query: str) -> Tuple[bool, str]:
    """
    Validate user input for safety and quality.
    
    Args:
        query: The user's research query
        
    Returns:
        Tuple of (is_valid, message)
    """
    # Check for empty input
    if not query or not query.strip():
        return False, "Please provide a research topic or question."
    
    # Check query length
    if len(query) > MAX_QUERY_LENGTH:
        return False, f"Query is too long. Please limit to {MAX_QUERY_LENGTH} characters."
    
    # Check for sensitive topics
    query_lower = query.lower()
    for topic in SENSITIVE_TOPICS:
        if topic in query_lower:
            return False, "This topic cannot be researched due to safety guidelines."
    
    return True, "Input validated successfully."


def validate_findings(findings: List[dict]) -> Tuple[bool, str]:
    """
    Validate research findings before summarization.
    
    Args:
        findings: List of research findings
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not findings:
        return False, "No research findings to summarize."
    
    if len(findings) < 2:
        return True, "Warning: Limited findings. Summary may be incomplete."
    
    return True, "Findings validated successfully."


def sanitize_output(text: str) -> str:
    """
    Sanitize output text to remove any potentially harmful content.
    
    Args:
        text: The text to sanitize
        
    Returns:
        Sanitized text
    """
    # Remove any potential script injection
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML tags (keep text content)
    text = re.sub(r'<[^>]+>', '', text)
    
    return text


def check_source_quality(url: str) -> str:
    """
    Assess the quality/reliability tier of a source.
    
    Args:
        url: The URL to check
        
    Returns:
        Quality tier: "high", "medium", or "low"
    """
    # High quality sources (research, government, established news)
    high_quality_domains = [
        ".gov", ".edu", "nature.com", "science.org",
        "reuters.com", "apnews.com", "bbc.com",
        "nytimes.com", "wsj.com", "economist.com",
        "arxiv.org", "ncbi.nlm.nih.gov"
    ]
    
    # Medium quality sources (established websites)
    medium_quality_domains = [
        "wikipedia.org", "medium.com", "forbes.com",
        "techcrunch.com", "wired.com", "theverge.com"
    ]
    
    url_lower = url.lower()
    
    for domain in high_quality_domains:
        if domain in url_lower:
            return "high"
    
    for domain in medium_quality_domains:
        if domain in url_lower:
            return "medium"
    
    return "low"


def should_continue_research(findings: List[dict], iteration: int) -> bool:
    """
    Determine if more research iterations are needed.
    
    Args:
        findings: Current research findings
        iteration: Current iteration number
        
    Returns:
        True if more research is needed, False otherwise
    """
    # Don't exceed max iterations
    if iteration >= MAX_ITERATIONS:
        return False
    
    # Need at least 3 findings for a good summary
    if len(findings) < 3:
        return True
    
    # Check if we have any high-quality sources
    high_quality_count = sum(
        1 for f in findings 
        if check_source_quality(f.get("source", "")) == "high"
    )
    
    if high_quality_count < 1 and iteration < 2:
        return True
    
    return False


class ResearchGuardrails:
    """
    Centralized guardrails manager for the research assistant.
    """
    
    def __init__(self):
        self.max_query_length = MAX_QUERY_LENGTH
        self.max_iterations = MAX_ITERATIONS
        self.max_search_queries = MAX_SEARCH_QUERIES
    
    def check_input(self, query: str) -> Tuple[bool, str]:
        """Validate user input."""
        return validate_input(query)
    
    def check_findings(self, findings: List[dict]) -> Tuple[bool, str]:
        """Validate research findings."""
        return validate_findings(findings)
    
    def sanitize(self, text: str) -> str:
        """Sanitize output text."""
        return sanitize_output(text)
    
    def should_continue(self, findings: List[dict], iteration: int) -> bool:
        """Check if more research is needed."""
        return should_continue_research(findings, iteration)
    
    def get_source_quality(self, url: str) -> str:
        """Get source quality tier."""
        return check_source_quality(url)
