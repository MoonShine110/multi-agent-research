# 🔬 Multi-Agent Research Assistant

A sophisticated AI-powered research assistant built with **LangGraph** that uses two collaborative agents to conduct web research and produce executive summaries.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **Multi-Agent System** | Research Agent + Summary Agent working together |
| 🔄 **LangGraph Orchestration** | Graph-based state machine with conditional loops |
| 🔍 **Web Search** | Real-time web search via DuckDuckGo |
| 💾 **Database Storage** | SQLite persistence for all research history |
| 📄 **File Export** | Export to Markdown, JSON, CSV, TXT |
| 🧵 **Thread Management** | Multiple conversation threads with memory |
| 🛡️ **Guardrails** | Input validation, source quality scoring |
| 📊 **LangSmith Tracing** | Optional observability and debugging |
| 🔌 **Flexible LLM** | Supports OpenAI, Anthropic Claude, and Ollama |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                              │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH ORCHESTRATOR                       │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  [START] → [Validator] → [Research] → [Quality Check]  │    │
│  │                              ↑              │           │    │
│  │                              └──────────────┘ (loop)    │    │
│  │                                             │           │    │
│  │                                    [Summary] → [END]    │    │
│  └────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   Research   │       │   Summary    │       │  Guardrails  │
│    Agent     │       │    Agent     │       │   & Safety   │
└──────────────┘       └──────────────┘       └──────────────┘
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/multi-agent-research.git
cd multi-agent-research
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env with your API keys
# See Configuration section below
```

### 5. Run the Application

```bash
python main.py
```

## ⚙️ Configuration

### Choose Your LLM Provider

Edit `.env` and set `LLM_PROVIDER` to one of: `openai`, `anthropic`, `ollama`

#### Option 1: OpenAI (Recommended)
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```
Get your key at: https://platform.openai.com/api-keys

#### Option 2: Anthropic Claude
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```
Get your key at: https://console.anthropic.com/

#### Option 3: Ollama (Free/Local)
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```
Install Ollama from: https://ollama.ai

Then pull a model:
```bash
ollama pull llama3.2
```

### Enable LangSmith Tracing (Optional)

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_your-key-here
LANGCHAIN_PROJECT=multi-agent-research
```
Get your key at: https://smith.langchain.com

## 📖 Usage

### Interactive Mode

```bash
python main.py
```

### Direct Query

```bash
python main.py "What are the latest developments in quantum computing?"
```

### Show Workflow Graph

```bash
python main.py --show-graph
```

## 🎮 Commands Reference

Once in interactive mode, use these commands:

### Research Commands
| Command | Description |
|---------|-------------|
| `<your question>` | Start new research |
| `more` | Expand on last research |
| `insights` | Show key insights |
| `sources` | List all sources |
| `export` | Save to markdown file |

### Thread Commands
| Command | Description |
|---------|-------------|
| `threads` | List all threads |
| `new` | Create new thread |
| `new <name>` | Create named thread |
| `switch <n>` | Switch to thread #n |
| `rename <name>` | Rename current thread |
| `history` | Show thread history |

### Database Commands
| Command | Description |
|---------|-------------|
| `db` | Show database stats |
| `db history` | Show all research |
| `db export csv` | Export to CSV |
| `db export txt` | Export to TXT |
| `db search <keyword>` | Search past research |

### Other Commands
| Command | Description |
|---------|-------------|
| `help` | Show help menu |
| `graph` | Show workflow graph |
| `quit` / `exit` | Exit program |

## 📁 Project Structure

```
multi-agent-research/
├── main.py                 # Entry point & CLI
├── requirements.txt        # Dependencies
├── .env.example           # Configuration template
├── README.md              # This file
├── SETUP.md               # Detailed setup guide
├── LICENSE                # MIT License
│
├── agents/                # AI Agents
│   ├── research_agent.py  # Web research agent
│   ├── summary_agent.py   # Summarization agent
│   └── prompts.py         # Agent prompts
│
├── graph/                 # LangGraph workflow
│   ├── workflow.py        # Graph definition
│   ├── nodes.py           # Node functions
│   └── state.py           # State schema
│
├── tools/                 # External tools
│   ├── llm_provider.py    # Flexible LLM selection
│   ├── search.py          # Web search
│   ├── database.py        # SQLite storage
│   ├── file_export.py     # File exports
│   └── rag.py             # Vector store cache
│
└── guardrails/            # Safety controls
    └── validators.py      # Input/output validation
```

## 🛡️ Safety Features

- **Input Validation**: Query length limits, sensitive topic filtering
- **Quality Control**: Minimum findings threshold, iteration limits
- **Source Scoring**: Prioritizes authoritative sources (.gov, .edu, etc.)
- **Output Sanitization**: Removes potentially harmful content

## 📊 Example Output

```
============================================================
📋 EXECUTIVE SUMMARY
============================================================

Quantum computing represents a paradigm shift in computational 
technology, utilizing quantum mechanical phenomena like 
superposition and entanglement...

------------------------------------------------------------
💡 KEY INSIGHTS
------------------------------------------------------------
  1. Quantum computers use qubits instead of classical bits
  2. Major players: IBM, Google, IonQ, Rigetti
  3. Current systems: 100-1000+ qubits
  4. Key applications: cryptography, drug discovery, optimization

------------------------------------------------------------
📚 SOURCES
------------------------------------------------------------
  • IBM Quantum Computing
    https://www.ibm.com/quantum
  • Nature: Quantum Supremacy
    https://www.nature.com/articles/...
============================================================
```

## 🔧 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "API key not found"
Make sure your `.env` file exists and contains valid keys:
```bash
cp .env.example .env
# Edit .env with your keys
```

### Ollama connection error
```bash
# Make sure Ollama is running
ollama serve

# Pull your model
ollama pull llama3.2
```

### Windows encoding errors
The project uses UTF-8 encoding. If you see encoding errors, ensure your terminal supports UTF-8.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) - Graph-based agent orchestration
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [DuckDuckGo](https://duckduckgo.com/) - Web search API

---

⭐ **Star this repo if you find it useful!** ⭐
