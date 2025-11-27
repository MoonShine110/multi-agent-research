"""
Summary Agent - Responsible for creating executive summaries

This agent:
1. Takes research findings from the Research Agent
2. Synthesizes them into a coherent executive summary
3. Extracts key insights and takeaways
"""

from typing import List, Dict
from langchain_core.messages import HumanMessage, SystemMessage

from .prompts import SUMMARY_AGENT_PROMPT
from tools.llm_provider import get_llm


class SummaryAgent:
    """Agent responsible for synthesizing research into executive summaries."""
    
    def __init__(self):
        """
        Initialize the Summary Agent.
        Uses the LLM provider configured in .env (openai, anthropic, or ollama)
        """
        self.llm = get_llm(
            temperature=0.4,  # Slightly higher for more natural writing
            max_tokens=4096
        )
        self.system_prompt = SUMMARY_AGENT_PROMPT
    
    def format_findings_for_summary(self, findings: List[Dict]) -> str:
        """
        Format research findings into a readable format for summarization.
        
        Args:
            findings: List of research findings from Research Agent
            
        Returns:
            Formatted string of findings
        """
        formatted = []
        for i, finding in enumerate(findings, 1):
            formatted.append(f"""
Finding {i}:
- Source: {finding.get('title', 'Unknown')}
- URL: {finding.get('source', 'N/A')}
- Content: {finding.get('content', 'No content')}
- Relevance: {finding.get('relevance', 'N/A')}
""")
        return "\n".join(formatted)
    
    def summarize(self, query: str, findings: List[Dict]) -> Dict:
        """
        Create an executive summary from research findings.
        
        Args:
            query: The original user query
            findings: Research findings from the Research Agent
            
        Returns:
            Dictionary containing:
            - executive_summary: The full summary text
            - key_insights: List of key insight bullet points
            - sources: List of sources used
        """
        if not findings:
            return {
                "executive_summary": "No research findings were available to summarize.",
                "key_insights": ["Unable to gather sufficient information on this topic."],
                "sources": []
            }
        
        # Format findings for the LLM
        findings_text = self.format_findings_for_summary(findings)
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""
Original Research Query: "{query}"

Research Findings:
{findings_text}

Please create an executive summary based on these findings. Remember to:
1. Synthesize the information into a coherent narrative
2. Highlight the most important insights
3. Cite sources for specific claims
4. Note any gaps or uncertainties

Format your response with clear sections:
- EXECUTIVE SUMMARY (2-3 paragraphs)
- KEY INSIGHTS (3-5 bullet points)
- SOURCES REFERENCED (list the sources)
""")
        ]
        
        response = self.llm.invoke(messages)
        content = response.content
        
        # Parse the response into sections
        executive_summary = ""
        key_insights = []
        sources = []
        
        # Extract executive summary
        if "EXECUTIVE SUMMARY" in content:
            parts = content.split("KEY INSIGHTS")
            summary_part = parts[0].replace("EXECUTIVE SUMMARY", "").strip()
            # Clean up any markdown formatting
            summary_part = summary_part.strip("# \n")
            executive_summary = summary_part
        
        # Extract key insights
        if "KEY INSIGHTS" in content:
            insights_start = content.find("KEY INSIGHTS")
            insights_end = content.find("SOURCES") if "SOURCES" in content else len(content)
            insights_text = content[insights_start:insights_end]
            
            # Parse bullet points
            for line in insights_text.split("\n"):
                line = line.strip()
                if line.startswith(("-", "•", "*", "1", "2", "3", "4", "5")):
                    # Clean up the bullet point
                    insight = line.lstrip("-•*0123456789. ")
                    if insight:
                        key_insights.append(insight)
        
        # Extract sources
        for finding in findings:
            source = finding.get("source", "")
            title = finding.get("title", "Unknown")
            if source:
                sources.append({"title": title, "url": source})
        
        # Fallback if parsing failed
        if not executive_summary:
            executive_summary = content
        
        if not key_insights:
            key_insights = ["See executive summary for details."]
        
        return {
            "executive_summary": executive_summary,
            "key_insights": key_insights[:5],  # Limit to 5 insights
            "sources": sources
        }
    
    def format_output(self, summary_data: Dict) -> str:
        """
        Format the summary data into a nice readable output.
        
        Args:
            summary_data: Dictionary with executive_summary, key_insights, sources
            
        Returns:
            Formatted string for display
        """
        output = []
        output.append("=" * 60)
        output.append("📋 EXECUTIVE SUMMARY")
        output.append("=" * 60)
        output.append("")
        output.append(summary_data.get("executive_summary", "No summary available."))
        output.append("")
        output.append("-" * 60)
        output.append("💡 KEY INSIGHTS")
        output.append("-" * 60)
        
        for i, insight in enumerate(summary_data.get("key_insights", []), 1):
            output.append(f"  {i}. {insight}")
        
        output.append("")
        output.append("-" * 60)
        output.append("📚 SOURCES")
        output.append("-" * 60)
        
        for source in summary_data.get("sources", []):
            output.append(f"  • {source.get('title', 'Unknown')}")
            output.append(f"    {source.get('url', 'N/A')}")
        
        output.append("")
        output.append("=" * 60)
        
        return "\n".join(output)
