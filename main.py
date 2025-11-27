#!/usr/bin/env python3
"""
Multi-Agent Research Assistant - Main Entry Point

This is the main file to run the research assistant.
It provides both a CLI interface and a programmatic API.

Usage:
    python main.py                          # Interactive mode
    python main.py "your research topic"    # Direct query mode
    python main.py --help                   # Show help
    python main.py --tracing                # Enable LangSmith tracing
"""

import sys
import os
import argparse
from typing import Optional
from uuid import uuid4
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()


def setup_tracing():
    """
    Setup LangSmith tracing based on .env configuration.
    
    LangSmith provides observability for your LLM applications:
    - Trace all LLM calls
    - Debug agent behavior
    - Monitor performance
    
    Configure in .env file:
        LANGCHAIN_TRACING_V2=true
        LANGCHAIN_API_KEY=your-api-key
        LANGCHAIN_PROJECT=your-project-name
    """
    # Check if tracing is enabled in .env
    tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true"
    api_key = os.getenv("LANGCHAIN_API_KEY", "")
    
    # Validate API key is not placeholder
    if api_key and "your" in api_key.lower():
        api_key = ""
    
    if tracing_enabled and api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        project = os.getenv("LANGCHAIN_PROJECT", "multi-agent-research")
        os.environ["LANGCHAIN_PROJECT"] = project
        print(f"📊 LangSmith tracing ENABLED (Project: {project})")
        print(f"   View traces at: https://smith.langchain.com")
        return True
    elif tracing_enabled and not api_key:
        print("⚠️  LANGCHAIN_TRACING_V2=true but LANGCHAIN_API_KEY not set")
        print("   Tracing disabled. Add your key to .env to enable.")
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        return False
    else:
        # Tracing disabled
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        return False


# Validate LLM provider configuration
from tools.llm_provider import validate_provider, get_provider_info

is_valid, message = validate_provider()
if not is_valid:
    print(f"❌ ERROR: {message}")
    print("\nConfigure your LLM provider in .env file:")
    print("  LLM_PROVIDER=openai    (or anthropic, ollama)")
    print("  OPENAI_API_KEY=sk-...")
    print("\nOr use Ollama for free local models:")
    print("  LLM_PROVIDER=ollama")
    print("  OLLAMA_MODEL=llama3.2")
    sys.exit(1)
else:
    provider_info = get_provider_info()
    print(f"✅ LLM Provider: {provider_info['provider'].upper()} ({provider_info['model']})")

from graph.workflow import get_research_graph, visualize_graph
from agents.summary_agent import SummaryAgent


def run_research(query: str, thread_id: Optional[str] = None) -> dict:
    """
    Run the research assistant on a query.
    
    Args:
        query: The research topic or question
        thread_id: Optional thread ID for conversation continuity
        
    Returns:
        Dictionary containing the final state with results
    """
    # Get the compiled graph
    app = get_research_graph()
    
    # Create a unique thread ID if not provided
    if thread_id is None:
        thread_id = str(uuid4())
    
    # Configuration for this run
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    
    # Initial state
    initial_state = {
        "query": query,
        "search_queries": [],
        "findings": [],
        "sources_consulted": 0,
        "research_complete": False,
        "executive_summary": "",
        "key_insights": [],
        "messages": [],
        "iteration_count": 0,
        "error": None
    }
    
    print(f"\n{'='*60}")
    print(f"🔬 MULTI-AGENT RESEARCH ASSISTANT")
    print(f"{'='*60}")
    print(f"Query: {query}")
    print(f"Thread ID: {thread_id}")
    print(f"{'='*60}")
    
    # Run the graph
    final_state = None
    for event in app.stream(initial_state, config):
        # Each event is a dict with the node name as key
        for node_name, node_output in event.items():
            if node_output:  # Only update if there's output
                if final_state is None:
                    final_state = initial_state.copy()
                final_state.update(node_output)
    
    return final_state or initial_state


def format_results(state: dict) -> str:
    """
    Format the results for display.
    
    Args:
        state: The final state from the graph
        
    Returns:
        Formatted string for display
    """
    summary_agent = SummaryAgent()
    
    # Build the summary data structure
    summary_data = {
        "executive_summary": state.get("executive_summary", "No summary available."),
        "key_insights": state.get("key_insights", []),
        "sources": [
            {"title": f.get("title", "Unknown"), "url": f.get("source", "N/A")}
            for f in state.get("findings", [])
        ]
    }
    
    return summary_agent.format_output(summary_data)


def interactive_mode():
    """Run the assistant in interactive mode with conversation memory and thread management."""
    
    # Thread management
    threads = {}  # thread_id -> {name, history, last_state}
    current_thread_id = str(uuid4())
    threads[current_thread_id] = {
        'name': 'Thread 1',
        'history': [],
        'last_state': None,
        'created': datetime.now().strftime('%H:%M:%S')
    }
    
    def get_current_thread():
        return threads[current_thread_id]
    
    def print_help():
        print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     🔬 Multi-Agent Research Assistant - Interactive      ║
    ╠══════════════════════════════════════════════════════════╣
    ║  Research Commands:                                      ║
    ║    - Type your research topic/question                   ║
    ║    - 'more' - Get more details on last research          ║
    ║    - 'insights' - Show key insights again                ║
    ║    - 'sources' - List all sources found                  ║
    ║    - 'export' - Save last research to file               ║
    ║                                                          ║
    ║  Thread Commands:                                        ║
    ║    - 'threads' - List all conversation threads           ║
    ║    - 'new' or 'new <name>' - Create a new thread         ║
    ║    - 'switch <number>' - Switch to a different thread    ║
    ║    - 'rename <name>' - Rename current thread             ║
    ║    - 'history' - Show current thread's history           ║
    ║                                                          ║
    ║  Other:                                                  ║
    ║    - 'graph' - Show the workflow graph                   ║
    ║    - 'help' - Show this help message                     ║
    ║    - 'quit' or 'exit' - Exit the program                 ║
    ╚══════════════════════════════════════════════════════════╝
        """)
    
    print_help()
    print(f"\n📌 Current Thread: {get_current_thread()['name']} (ID: {current_thread_id[:8]}...)")
    
    while True:
        try:
            thread = get_current_thread()
            prompt = f"\n[{thread['name']}] 🔍 Enter topic or command: "
            user_input = input(prompt).strip()
            
            if not user_input:
                continue
            
            # === EXIT COMMANDS ===
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            # === HELP ===
            if user_input.lower() == 'help':
                print_help()
                continue
            
            # === GRAPH ===
            if user_input.lower() == 'graph':
                visualize_graph(None)
                continue
            
            # === DATABASE COMMANDS ===
            if user_input.lower().startswith('db'):
                from tools.database import get_database
                db = get_database()
                
                cmd = user_input.lower().strip()
                
                # Show stats
                if cmd == 'db':
                    stats = db.get_statistics()
                    print("\n📊 Database Statistics:")
                    print(f"   Total Queries: {stats['total_queries']}")
                    print(f"   Total Findings: {stats['total_findings']}")
                    print(f"   Total Summaries: {stats['total_summaries']}")
                    print(f"   Database Path: {stats['database_path']}")
                    continue
                
                # Show full history
                if cmd == 'db history':
                    history = db.get_full_history()
                    if history:
                        print(f"\n📜 Research History ({len(history)} records):")
                        print("-" * 60)
                        for item in history[:20]:
                            print(f"   [{item['id']}] {item['timestamp']}")
                            query_preview = item['query'][:50] if item['query'] else 'N/A'
                            print(f"       Query: {query_preview}...")
                            print(f"       Status: {item['status']} | Findings: {item['finding_count']}")
                        if len(history) > 20:
                            print(f"   ... and {len(history) - 20} more records")
                    else:
                        print("\n📜 No research history in database yet.")
                    continue
                
                # Export to CSV
                if cmd == 'db export csv':
                    filepath = db.export_to_csv()
                    print(f"✅ Exported to: {filepath}")
                    continue
                
                # Export to TXT
                if cmd == 'db export txt':
                    filepath = db.export_to_txt()
                    print(f"✅ Exported to: {filepath}")
                    continue
                
                # Search
                if cmd.startswith('db search '):
                    keyword = user_input[10:].strip()
                    results = db.search_past_research(keyword)
                    if results:
                        print(f"\n🔍 Search Results for '{keyword}' ({len(results)} found):")
                        for r in results:
                            query_preview = r['query'][:50] if r['query'] else 'N/A'
                            print(f"   [{r['id']}] {query_preview}...")
                    else:
                        print(f"\n🔍 No results found for '{keyword}'")
                    continue
                
                print("❌ Unknown db command. Try: db, db history, db export csv, db export txt, db search <keyword>")
                continue
            
            # === THREAD COMMANDS ===
            
            # List all threads
            if user_input.lower() == 'threads':
                print("\n🧵 All Threads:")
                for i, (tid, tdata) in enumerate(threads.items(), 1):
                    current = " 👈 (current)" if tid == current_thread_id else ""
                    query_count = len(tdata['history'])
                    print(f"   {i}. {tdata['name']} - {query_count} queries - created {tdata['created']}{current}")
                continue
            
            # Create new thread
            if user_input.lower().startswith('new'):
                parts = user_input.split(' ', 1)
                new_name = parts[1] if len(parts) > 1 else f"Thread {len(threads) + 1}"
                new_id = str(uuid4())
                threads[new_id] = {
                    'name': new_name,
                    'history': [],
                    'last_state': None,
                    'created': datetime.now().strftime('%H:%M:%S')
                }
                current_thread_id = new_id
                print(f"\n✨ Created and switched to new thread: {new_name}")
                continue
            
            # Switch thread
            if user_input.lower().startswith('switch '):
                try:
                    thread_num = int(user_input.split()[1]) - 1
                    thread_ids = list(threads.keys())
                    if 0 <= thread_num < len(thread_ids):
                        current_thread_id = thread_ids[thread_num]
                        print(f"\n🔄 Switched to: {threads[current_thread_id]['name']}")
                        # Show thread history summary
                        hist = threads[current_thread_id]['history']
                        if hist:
                            print(f"   Last query: {hist[-1]}")
                    else:
                        print(f"❌ Invalid thread number. Use 1-{len(threads)}")
                except (ValueError, IndexError):
                    print("❌ Usage: switch <number>")
                continue
            
            # Rename thread
            if user_input.lower().startswith('rename '):
                new_name = user_input.split(' ', 1)[1]
                threads[current_thread_id]['name'] = new_name
                print(f"✏️ Thread renamed to: {new_name}")
                continue
            
            # === RESEARCH COMMANDS ===
            
            # Show history
            if user_input.lower() == 'history':
                if thread['history']:
                    print(f"\n📜 History for '{thread['name']}':")
                    for i, q in enumerate(thread['history'], 1):
                        print(f"   {i}. {q}")
                else:
                    print("\n📜 No research history in this thread yet.")
                continue
            
            # Show insights
            if user_input.lower() == 'insights':
                if thread['last_state']:
                    print("\n💡 Key Insights from Last Research:")
                    for i, insight in enumerate(thread['last_state'].get('key_insights', []), 1):
                        print(f"   {i}. {insight}")
                else:
                    print("❌ No research in this thread yet.")
                continue
            
            # Show sources
            if user_input.lower() == 'sources':
                if thread['last_state']:
                    print("\n📚 Sources from Last Research:")
                    for finding in thread['last_state'].get('findings', []):
                        print(f"   • {finding.get('title', 'Unknown')}")
                        print(f"     {finding.get('source', 'N/A')}")
                else:
                    print("❌ No research in this thread yet.")
                continue
            
            # Export
            if user_input.lower() == 'export':
                if thread['last_state']:
                    from tools.file_export import get_exporter
                    exporter = get_exporter()
                    filepath = exporter.export_markdown(
                        thread['last_state'].get('query', ''),
                        thread['last_state'].get('executive_summary', ''),
                        thread['last_state'].get('key_insights', []),
                        thread['last_state'].get('findings', [])
                    )
                    print(f"\n📄 Exported to: {filepath}")
                else:
                    print("❌ No research to export in this thread.")
                continue
            
            # More details
            if user_input.lower() == 'more':
                if thread['last_state']:
                    original_query = thread['last_state'].get('query', '')
                    user_input = f"More details about: {original_query}"
                    print(f"   🔄 Expanding on: {original_query}")
                else:
                    print("❌ No previous research to expand on.")
                    continue
            
            # === RUN RESEARCH ===
            
            # Check if this is a follow-up question
            if thread['last_state'] and is_followup_question(user_input):
                context = thread['last_state'].get('executive_summary', '')[:500]
                enhanced_query = f"{user_input} (Context: {context})"
                print(f"   💭 Detected follow-up question, using context from last research")
            else:
                enhanced_query = user_input
            
            # Run research with current thread ID
            final_state = run_research(enhanced_query, current_thread_id)
            
            # Store in thread
            final_state['query'] = user_input  # Store original query
            thread['last_state'] = final_state
            thread['history'].append(user_input)
            
            # Display results
            print(format_results(final_state))
            
            # Prompt for follow-up
            print(f"\n💡 Tip: Ask follow-ups, or type 'threads' to manage conversations")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again with a different query.")


def is_followup_question(query: str) -> bool:
    """
    Detect if a query is a follow-up question.
    
    Follow-up indicators:
    - Starts with pronouns like "what about", "how about", "and", "also"
    - References "it", "this", "that", "they"
    - Short queries that assume context
    """
    query_lower = query.lower().strip()
    
    followup_starters = [
        'what about', 'how about', 'and ', 'also ', 'but ',
        'tell me more', 'more on', 'expand on', 'elaborate',
        'why', 'how does', 'what if', 'can you explain',
        'regarding', 'concerning', 'about the', 'on the topic'
    ]
    
    # Check for follow-up starters
    for starter in followup_starters:
        if query_lower.startswith(starter):
            return True
    
    # Check for pronouns that reference previous context
    context_words = ['it', 'this', 'that', 'they', 'them', 'those', 'these']
    words = query_lower.split()
    if len(words) <= 5:  # Short queries likely need context
        for word in words:
            if word in context_words:
                return True
    
    return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Research Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                                    # Interactive mode
    python main.py "latest AI developments"           # Direct query
    python main.py --show-graph                       # Show workflow graph
    python main.py --tracing                          # Enable LangSmith tracing
    python main.py "AI trends"                         # Query directly
        """
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="Research topic or question (optional, enters interactive mode if not provided)"
    )
    
    parser.add_argument(
        "--show-graph",
        action="store_true",
        help="Display the workflow graph and exit"
    )
    
    args = parser.parse_args()
    
    # Setup tracing from .env (automatic)
    tracing_enabled = setup_tracing()
    
    if args.show_graph:
        visualize_graph(None)
        return
    
    if args.query:
        # Direct query mode
        final_state = run_research(args.query)
        print(format_results(final_state))
    else:
        # Interactive mode
        if tracing_enabled:
            print("\n🔍 All interactions will be traced to LangSmith\n")
        interactive_mode()


if __name__ == "__main__":
    main()
