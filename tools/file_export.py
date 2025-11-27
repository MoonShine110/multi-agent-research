"""
File Export Module - Save Research Results to Files

This module handles exporting research results to various file formats:
- Markdown (.md) - For readable reports
- JSON (.json) - For programmatic access
- Text (.txt) - For simple text output

WHY FILE EXPORT?
- Deliverable output for stakeholders
- Archive research for later reference
- Share findings across teams
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class FileExporter:
    """
    Handles exporting research results to files.
    """
    
    def __init__(self, output_dir: str = "./research_outputs"):
        """
        Initialize the file exporter.
        
        Args:
            output_dir: Directory to save output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_filename(self, query: str, extension: str) -> str:
        """Generate a filename from query and timestamp."""
        # Clean the query for use as filename
        clean_query = "".join(c if c.isalnum() or c == " " else "_" for c in query)
        clean_query = clean_query[:50].strip().replace(" ", "_")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{clean_query}_{timestamp}.{extension}"
    
    def export_markdown(
        self,
        query: str,
        executive_summary: str,
        key_insights: List[str],
        findings: List[Dict],
        filename: Optional[str] = None
    ) -> str:
        """
        Export research results as a Markdown file.
        
        Returns:
            Path to the created file
        """
        if filename is None:
            filename = self._generate_filename(query, "md")
        
        filepath = self.output_dir / filename
        
        # Build markdown content
        content = f"""# Research Report

## Query
{query}

## Executive Summary
{executive_summary}

## Key Insights
"""
        for i, insight in enumerate(key_insights, 1):
            content += f"{i}. {insight}\n"
        
        content += """
## Sources
"""
        for finding in findings:
            content += f"- **{finding.get('title', 'Unknown')}**\n"
            content += f"  - URL: {finding.get('source', 'N/A')}\n"
            content += f"  - Relevance: {finding.get('relevance', 'N/A')}\n\n"
        
        content += f"""
---
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Multi-Agent Research Assistant*
"""
        
        filepath.write_text(content, encoding='utf-8')
        print(f"   📄 Exported to: {filepath}")
        return str(filepath)
    
    def export_json(
        self,
        query: str,
        executive_summary: str,
        key_insights: List[str],
        findings: List[Dict],
        filename: Optional[str] = None
    ) -> str:
        """
        Export research results as a JSON file.
        
        Returns:
            Path to the created file
        """
        if filename is None:
            filename = self._generate_filename(query, "json")
        
        filepath = self.output_dir / filename
        
        data = {
            "query": query,
            "executive_summary": executive_summary,
            "key_insights": key_insights,
            "findings": findings,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "tool": "Multi-Agent Research Assistant"
            }
        }
        
        filepath.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"   📄 Exported to: {filepath}")
        return str(filepath)
    
    def export_text(
        self,
        query: str,
        executive_summary: str,
        key_insights: List[str],
        findings: List[Dict],
        filename: Optional[str] = None
    ) -> str:
        """
        Export research results as a plain text file.
        
        Returns:
            Path to the created file
        """
        if filename is None:
            filename = self._generate_filename(query, "txt")
        
        filepath = self.output_dir / filename
        
        content = f"""RESEARCH REPORT
{'=' * 60}

QUERY: {query}

{'=' * 60}
EXECUTIVE SUMMARY
{'=' * 60}

{executive_summary}

{'=' * 60}
KEY INSIGHTS
{'=' * 60}

"""
        for i, insight in enumerate(key_insights, 1):
            content += f"  {i}. {insight}\n"
        
        content += f"""
{'=' * 60}
SOURCES
{'=' * 60}

"""
        for finding in findings:
            content += f"  * {finding.get('title', 'Unknown')}\n"
            content += f"    URL: {finding.get('source', 'N/A')}\n\n"
        
        content += f"""
{'=' * 60}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Tool: Multi-Agent Research Assistant
"""
        
        filepath.write_text(content, encoding='utf-8')
        print(f"   📄 Exported to: {filepath}")
        return str(filepath)
    
    def export_all_formats(
        self,
        query: str,
        executive_summary: str,
        key_insights: List[str],
        findings: List[Dict]
    ) -> Dict[str, str]:
        """
        Export to all supported formats.
        
        Returns:
            Dictionary mapping format to filepath
        """
        return {
            "markdown": self.export_markdown(query, executive_summary, key_insights, findings),
            "json": self.export_json(query, executive_summary, key_insights, findings),
            "text": self.export_text(query, executive_summary, key_insights, findings)
        }


# Global exporter instance
_exporter_instance = None


def get_exporter(output_dir: str = "./research_outputs") -> FileExporter:
    """Get or create the file exporter singleton."""
    global _exporter_instance
    if _exporter_instance is None:
        _exporter_instance = FileExporter(output_dir)
    return _exporter_instance
