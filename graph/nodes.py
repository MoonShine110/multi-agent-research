"""
LangGraph Nodes for Multi-Agent Research Assistant

Nodes are the "workers" in a LangGraph workflow. Each node:
1. Receives the current state
2. Does some work
3. Returns updates to the state

Think of nodes as functions that process and transform the shared state.

INTEGRATIONS:
- RAG: Check for similar past research before web search
- Database: Store all queries, findings, and summaries
- File Export: Save final results to files
"""

from typing import Dict, Any
from graph.state import ResearchState
from agents.research_agent import ResearchAgent
from agents.summary_agent import SummaryAgent
from guardrails.validators import ResearchGuardrails

# Import new integrations
from tools.database import get_database
from tools.file_export import get_exporter

# Try to import RAG (may fail if chromadb not installed)
try:
    from tools.rag import create_rag
    rag_available = True
except ImportError:
    rag_available = False
    print("⚠️ RAG not available (chromadb not installed)")


# Initialize components
research_agent = ResearchAgent()
summary_agent = SummaryAgent()
guardrails = ResearchGuardrails()
database = get_database()
file_exporter = get_exporter()

# Initialize RAG if available
if rag_available:
    try:
        rag = create_rag(use_persistent=False)  # Use simple in-memory RAG
    except:
        rag = None
else:
    rag = None


def input_validator_node(state: ResearchState) -> Dict[str, Any]:
    """
    Node 1: Validate user input before processing.
    
    This is a guardrail node that ensures the query is safe and valid.
    Also saves the query to the database.
    """
    print("\n🛡️  [Input Validator] Checking query...")
    
    query = state.get("query", "")
    is_valid, message = guardrails.check_input(query)
    
    if not is_valid:
        print(f"   ❌ Validation failed: {message}")
        return {
            "error": message,
            "research_complete": True  # Skip to end
        }
    
    # Save query to database
    query_id = database.save_query(query)
    print(f"   ✅ Query validated and saved (ID: {query_id})")
    
    return {
        "error": None,
        "iteration_count": 0,
        "query_id": query_id  # Store for later use
    }


def rag_check_node(state: ResearchState) -> Dict[str, Any]:
    """
    Node 1.5: Check RAG for similar past research.
    
    This node checks if we have cached research that might be relevant,
    potentially saving time and API calls.
    """
    print("\n🔍 [RAG Check] Searching for similar past research...")
    
    if rag is None:
        print("   ⚠️ RAG not available, skipping cache check")
        return {"cached_findings": []}
    
    query = state["query"]
    similar = rag.search_similar(query, n_results=3)
    
    if similar:
        print(f"   📚 Found {len(similar)} relevant cached findings")
        return {"cached_findings": similar}
    else:
        print("   📭 No cached findings found")
        return {"cached_findings": []}


def research_node(state: ResearchState) -> Dict[str, Any]:
    """
    Node 2: Research Agent conducts web research.
    
    This node:
    - Generates search queries
    - Executes web searches
    - Extracts and structures findings
    - Caches findings in RAG
    - Saves findings to database
    """
    print("\n🔬 [Research Agent] Starting research...")
    
    # Check for errors from previous nodes
    if state.get("error"):
        return {}
    
    query = state["query"]
    current_iteration = state.get("iteration_count", 0)
    
    print(f"   📝 Research iteration: {current_iteration + 1}")
    
    # Conduct research
    research_results = research_agent.research(query)
    
    # Merge with any existing findings (for multi-iteration research)
    existing_findings = state.get("findings", [])
    cached_findings = state.get("cached_findings", [])
    new_findings = research_results.get("findings", [])
    
    # Deduplicate findings by source URL
    seen_sources = {f.get("source") for f in existing_findings}
    unique_new = [f for f in new_findings if f.get("source") not in seen_sources]
    
    all_findings = existing_findings + unique_new
    
    # Add cached findings if this is the first iteration
    if current_iteration == 0 and cached_findings:
        for cf in cached_findings:
            if cf.get("source") not in seen_sources:
                all_findings.append(cf)
    
    print(f"   📊 Total findings: {len(all_findings)}")
    
    # Cache findings in RAG
    if rag and unique_new:
        rag.add_findings(query, unique_new)
    
    # Save findings to database
    query_id = state.get("query_id")
    if query_id and unique_new:
        database.save_findings(query_id, unique_new)
    
    return {
        "search_queries": research_results.get("search_queries", []),
        "findings": all_findings,
        "sources_consulted": len(all_findings),
        "iteration_count": current_iteration + 1
    }


def quality_check_node(state: ResearchState) -> Dict[str, Any]:
    """
    Node 3: Check if research quality is sufficient.
    
    This is a decision node that determines if we need more research
    or can proceed to summarization.
    """
    print("\n🔍 [Quality Check] Evaluating research quality...")
    
    findings = state.get("findings", [])
    iteration = state.get("iteration_count", 0)
    
    is_valid, message = guardrails.check_findings(findings)
    print(f"   {message}")
    
    # Check if we should continue researching
    needs_more = guardrails.should_continue(findings, iteration)
    
    if needs_more:
        print(f"   🔄 More research needed (iteration {iteration})")
    else:
        print(f"   ✅ Research sufficient ({len(findings)} findings)")
    
    return {
        "research_complete": not needs_more
    }


def summary_node(state: ResearchState) -> Dict[str, Any]:
    """
    Node 4: Summary Agent creates executive summary.
    
    This node synthesizes all research findings into a coherent
    executive summary with key insights.
    Also saves the summary to the database.
    """
    print("\n📝 [Summary Agent] Creating executive summary...")
    
    # Check for errors
    if state.get("error"):
        return {
            "executive_summary": f"Error: {state['error']}",
            "key_insights": []
        }
    
    query = state["query"]
    findings = state.get("findings", [])
    
    # Generate summary
    summary_result = summary_agent.summarize(query, findings)
    
    executive_summary = summary_result.get("executive_summary", "")
    key_insights = summary_result.get("key_insights", [])
    
    print(f"   ✅ Summary created with {len(key_insights)} insights")
    
    # Save summary to database
    query_id = state.get("query_id")
    if query_id:
        database.save_summary(query_id, executive_summary, key_insights)
    
    return {
        "executive_summary": executive_summary,
        "key_insights": key_insights
    }


def output_formatter_node(state: ResearchState) -> Dict[str, Any]:
    """
    Node 5: Format and export the final output.
    
    This node prepares the final output for display and
    exports results to files.
    """
    print("\n📤 [Output Formatter] Preparing final output...")
    
    # Export to file
    query = state.get("query", "")
    executive_summary = state.get("executive_summary", "")
    key_insights = state.get("key_insights", [])
    findings = state.get("findings", [])
    
    if executive_summary and not state.get("error"):
        # Export to markdown file
        filepath = file_exporter.export_markdown(
            query, executive_summary, key_insights, findings
        )
        print(f"   📄 Report saved to: {filepath}")
        return {"output_file": filepath}
    
    return {}


# Conditional edge function for routing
def should_continue_research(state: ResearchState) -> str:
    """
    Conditional routing function.
    
    Returns:
        "research" - if more research is needed
        "summarize" - if ready to summarize
    """
    if state.get("error"):
        return "summarize"  # Skip to end on error
    
    if state.get("research_complete", False):
        return "summarize"
    
    return "research"
