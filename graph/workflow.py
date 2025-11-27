"""
LangGraph Workflow for Multi-Agent Research Assistant

This is the heart of the system - it defines the graph structure
that orchestrates our agents.

Graph Structure:
    START
      │
      ▼
    [input_validator]
      │
      ▼
    [research] ◄────┐
      │             │
      ▼             │
    [quality_check]─┘ (loops back if more research needed)
      │
      ▼
    [summary]
      │
      ▼
    [output]
      │
      ▼
     END
"""

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

from graph.state import ResearchState
from graph.nodes import (
    input_validator_node,
    research_node,
    quality_check_node,
    summary_node,
    output_formatter_node,
    should_continue_research
)


def create_research_graph():
    """
    Create and compile the research assistant graph.
    
    Returns:
        Compiled LangGraph workflow
    """
    # Initialize the graph with our state schema
    workflow = StateGraph(ResearchState)
    
    # ============================================
    # ADD NODES (the agents/workers)
    # ============================================
    
    workflow.add_node("input_validator", input_validator_node)
    workflow.add_node("research", research_node)
    workflow.add_node("quality_check", quality_check_node)
    workflow.add_node("summary", summary_node)
    workflow.add_node("output", output_formatter_node)
    
    # ============================================
    # ADD EDGES (the flow between nodes)
    # ============================================
    
    # Start -> Input Validator
    workflow.add_edge(START, "input_validator")
    
    # Input Validator -> Research
    workflow.add_edge("input_validator", "research")
    
    # Research -> Quality Check
    workflow.add_edge("research", "quality_check")
    
    # Quality Check -> Conditional routing
    # This is where the magic happens - we can loop back for more research!
    workflow.add_conditional_edges(
        "quality_check",
        should_continue_research,
        {
            "research": "research",    # Loop back for more research
            "summarize": "summary"     # Proceed to summary
        }
    )
    
    # Summary -> Output
    workflow.add_edge("summary", "output")
    
    # Output -> END
    workflow.add_edge("output", END)
    
    # ============================================
    # COMPILE WITH MEMORY (for conversation history)
    # ============================================
    
    # MemorySaver allows us to save state between runs
    # This enables follow-up questions!
    memory = MemorySaver()
    
    # Compile the graph
    app = workflow.compile(checkpointer=memory)
    
    return app


def visualize_graph(app):
    """
    Print a text representation of the graph structure.
    
    Args:
        app: Compiled LangGraph application
    """
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║        Multi-Agent Research Assistant - Graph            ║
    ╠══════════════════════════════════════════════════════════╣
    ║                                                          ║
    ║                      [START]                             ║
    ║                         │                                ║
    ║                         ▼                                ║
    ║               ┌─────────────────┐                        ║
    ║               │ Input Validator │ ← Guardrails           ║
    ║               └────────┬────────┘                        ║
    ║                        │                                 ║
    ║                        ▼                                 ║
    ║               ┌─────────────────┐                        ║
    ║           ┌──▶│ Research Agent  │ ← Web Search           ║
    ║           │   └────────┬────────┘                        ║
    ║           │            │                                 ║
    ║           │            ▼                                 ║
    ║           │   ┌─────────────────┐                        ║
    ║           └───│ Quality Check   │ ← Loop if needed       ║
    ║               └────────┬────────┘                        ║
    ║                        │                                 ║
    ║                        ▼                                 ║
    ║               ┌─────────────────┐                        ║
    ║               │ Summary Agent   │ ← Synthesize           ║
    ║               └────────┬────────┘                        ║
    ║                        │                                 ║
    ║                        ▼                                 ║
    ║               ┌─────────────────┐                        ║
    ║               │ Output Format   │                        ║
    ║               └────────┬────────┘                        ║
    ║                        │                                 ║
    ║                        ▼                                 ║
    ║                      [END]                               ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)


# Create a singleton instance
research_graph = None

def get_research_graph():
    """Get or create the research graph singleton."""
    global research_graph
    if research_graph is None:
        research_graph = create_research_graph()
    return research_graph
