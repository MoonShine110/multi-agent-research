"""
Research Agent - Responsible for web research

This agent:
1. Takes a user query
2. Generates effective search queries
3. Executes searches
4. Extracts and structures findings
"""

import json
from typing import List, Dict
from langchain_core.messages import HumanMessage, SystemMessage

from .prompts import RESEARCH_AGENT_PROMPT, QUERY_GENERATOR_PROMPT
from tools.llm_provider import get_llm
from tools.search import web_search_multiple


class ResearchAgent:
    """Agent responsible for conducting web research."""
    
    def __init__(self):
        """
        Initialize the Research Agent.
        Uses the LLM provider configured in .env (openai, anthropic, or ollama)
        """
        self.llm = get_llm(
            temperature=0.3,  # Lower temperature for more focused research
            max_tokens=4096
        )
        self.system_prompt = RESEARCH_AGENT_PROMPT
    
    def generate_search_queries(self, user_query: str) -> List[str]:
        """
        Generate effective search queries from the user's question.
        
        Args:
            user_query: The original user question/topic
            
        Returns:
            List of search query strings
        """
        messages = [
            SystemMessage(content=QUERY_GENERATOR_PROMPT),
            HumanMessage(content=f"Research topic: {user_query}")
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            # Parse the JSON array of queries
            queries = json.loads(response.content)
            if isinstance(queries, list):
                return queries[:5]  # Limit to 5 queries
        except json.JSONDecodeError:
            # Fallback: use the query as-is
            pass
        
        # Default: return variations of the original query
        return [
            user_query,
            f"{user_query} latest news",
            f"{user_query} research",
        ]
    
    def analyze_results(self, query: str, search_results: List[Dict]) -> List[Dict]:
        """
        Analyze search results and extract relevant findings.
        
        Args:
            query: The original user query
            search_results: Raw search results from web search
            
        Returns:
            List of structured findings
        """
        if not search_results:
            return []
        
        # Format results for the LLM
        results_text = "\n\n".join([
            f"Source: {r['title']}\nURL: {r['link']}\nContent: {r['snippet']}"
            for r in search_results
        ])
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""
Analyze these search results for the query: "{query}"

Search Results:
{results_text}

Extract the most relevant findings. For each finding, provide:
1. The source URL
2. The title
3. Key content/facts extracted
4. Why it's relevant to the query

Format your response as a JSON array of objects with keys: source, title, content, relevance
""")
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            # Try to parse JSON from response
            content = response.content
            # Find JSON array in response
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end > start:
                findings = json.loads(content[start:end])
                return findings
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Fallback: convert raw results to findings format
        return [
            {
                "source": r["link"],
                "title": r["title"],
                "content": r["snippet"],
                "relevance": "Found in search results"
            }
            for r in search_results[:5]
        ]
    
    def research(self, query: str) -> Dict:
        """
        Conduct full research on a topic.
        
        Args:
            query: The user's research question/topic
            
        Returns:
            Dictionary containing:
            - search_queries: Queries used
            - findings: Structured research findings
            - sources_consulted: Number of sources checked
        """
        # Step 1: Generate search queries
        search_queries = self.generate_search_queries(query)
        print(f"📝 Generated {len(search_queries)} search queries")
        
        # Step 2: Execute searches
        search_results = web_search_multiple(search_queries, max_results_per_query=3)
        print(f"🔍 Found {len(search_results)} search results")
        
        # Step 3: Analyze and structure findings
        findings = self.analyze_results(query, search_results)
        print(f"📊 Extracted {len(findings)} relevant findings")
        
        return {
            "search_queries": search_queries,
            "findings": findings,
            "sources_consulted": len(search_results)
        }
