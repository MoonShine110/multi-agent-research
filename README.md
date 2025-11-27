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
. Do not forget to remove the .example extension 
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
  
## Example Input

```
(multirag) E:\project\multi-agent-research>python main.py
✅ LLM Provider: OPENAI (gpt-4o-mini)
🤖 Using OpenAI: gpt-4o-mini
🤖 Using OpenAI: gpt-4o-mini
   📁 Database initialized
📊 LangSmith tracing ENABLED (Project: langchain-course)
   View traces at: https://smith.langchain.com

🔍 All interactions will be traced to LangSmith


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


📌 Current Thread: Thread 1 (ID: af5de548...)

[Thread 1] 🔍 Enter topic or command: Tell me about gixxersf250
```

## 📊 Example Output

```
📤 [Output Formatter] Preparing final output...
   📄 Exported to: research_outputs\Tell_me_about_gixxersf250_20251127_232126.md
   📄 Report saved to: research_outputs\Tell_me_about_gixxersf250_20251127_232126.md
🤖 Using OpenAI: gpt-4o-mini
============================================================
📋 EXECUTIVE SUMMARY
============================================================

The Suzuki Gixxer SF 250 is a popular choice among entry-level sports bikes, known for its blend of performance, comfort, and style. With a robust engine producing 26.5 HP and 22.2 Nm of torque, the bike is designed to cater to both new and experienced riders. Over the years, it has garnered positive feedback from users, highlighting its reliability and fuel efficiency, making it an attractive option for daily commuting and weekend rides alike.

User reviews and ownership experiences reveal that the Gixxer SF 250 excels in comfort and handling, with many riders appreciating its performance over extended distances. The bike's aesthetic appeal has also been enhanced with new color schemes and compliance with OBD-2B regulations in the latest models, reflecting Suzuki's commitment to innovation and customer satisfaction. However, potential buyers should consider the competitive landscape, as the Gixxer SF 250 faces rivals that may offer similar specifications and features.

------------------------------------------------------------
💡 KEY INSIGHTS
------------------------------------------------------------
  1. Performance Specifications**: The 2023 Gixxer SF 250 features a single-cylinder, four-stroke engine generating 26.5 HP at 9300 RPM and 22.2 Nm at 7300 RPM, providing a solid performance for its class (Source: Ultimate Specs).
  2. User Satisfaction**: With 140 user reviews, the Gixxer SF 250 is praised for its fuel efficiency (approximately 36 kmpl) and comfort, making it suitable for both commuting and longer rides (Source: BikeDekho).
  3. Market Positioning**: The Gixxer SF 250 is positioned competitively in the entry-level sports bike segment, appealing to a broad audience due to its performance and affordability, with an on-road price of approximately Rs 2.36 lakh in Delhi (Source: Maxabout).
  4. Aesthetic Updates**: The latest model has introduced new color schemes and features, enhancing its visual appeal and compliance with updated environmental regulations (Source: BikeDekho).
  5. Comparative Insights**: A comparison with the Gixxer 250 highlights differences in aerodynamics and riding position, aiding prospective buyers in making informed decisions (Source: Zigwheels).

------------------------------------------------------------
📚 SOURCES
------------------------------------------------------------
  • Life with my Suzuki Gixxer SF 250 after riding 35000 km in 3 years
    https://www.team-bhp.com/news/life-my-suzuki-gixxer-sf-250-after-riding-35000-km-3-years
  • Suzuki Gixxer SF 250 [2020-2024] User Reviews
    https://www.bikedekho.com/suzuki/gixxer-sf-250-2020-2024/reviews
  • Suzuki Gixxer 250 & Gixxer SF 250 Review | Motorcycle Test
    https://www.mcnews.com.au/suzuki-gixxer-250-gixxer-sf-250-review-motorcycle-test/
  • Suzuki Gixxer 250 Colour: Suzuki Gixxer 250 and Gixxer Series Motorcycles Launched in New Colour Schemes
    https://economictimes.indiatimes.com/news/new-updates/suzuki-gixxer-250-and-gixxer-series-motorcycles-launched-in-new-colour-schemes/articleshow/97732517.cms
  • Suzuki Gixxer 250 vs Suzuki Gixxer SF - Compare Prices, Specs...
    https://www.zigwheels.com/bike-comparison/suzuki-gixxer-250-vs-suzuki-gixxer-sf
  • Suzuki Gixxer SF 250 | 250cc Bike Price & Specifications
    https://www.suzukimotorcycle.co.in/product-details/gixxer-sf-250
  • 2023 Suzuki Gixxer SF 250 Technical Specifications - Ultimate Specs
    https://www.ultimatespecs.com/motorcycles-specs/suzuki/suzuki-gixxer-sf-250-2023
  • Updated Suzuki Gixxer SF 250: What's New?
    https://www.bikedekho.com/news/updated-suzuki-gixxer-sf-250-whats-new-17443
  • Compare Suzuki Gixxer SF 250 vs Suzuki Gixxer 250 vs Bajaj
    https://autos.maxabout.com/bikes/compare/suzuki-gixxer-sf-250-vs-suzuki-gixxer-250-vs-bajaj

============================================================

💡 Tip: Ask follow-ups, or type 'threads' to manage conversations

[Thread 1] 🔍 Enter topic or command:
```

## Langsmith Trace (if enabled) 

<img width="1278" height="1275" alt="image" src="https://github.com/user-attachments/assets/2ea82193-2c75-4504-94a5-82db2b6f3e07" />

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
