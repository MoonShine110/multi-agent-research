# 📋 Detailed Setup Guide

This guide walks you through setting up the Multi-Agent Research Assistant step by step.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [LLM Provider Setup](#llm-provider-setup)
6. [LangSmith Tracing Setup](#langsmith-tracing-setup)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Software | Version | Download |
|----------|---------|----------|
| Python | 3.10 or higher | [python.org](https://python.org) |
| pip | Latest | Included with Python |
| Git | Any | [git-scm.com](https://git-scm.com) |

### Verify Installation

```bash
# Check Python version
python --version
# Should show: Python 3.10.x or higher

# Check pip
pip --version
```

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/multi-agent-research.git
cd multi-agent-research
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

**Basic installation (OpenAI only):**
```bash
pip install -r requirements.txt
```

**For Anthropic Claude:**
```bash
pip install -r requirements.txt
pip install langchain-anthropic
```

**For Ollama (local/free):**
```bash
pip install -r requirements.txt
pip install langchain-ollama
```

### Step 4: Create Configuration File

```bash
# Copy the example configuration
cp .env.example .env
```

Now edit `.env` with your preferred text editor.

---

## Configuration

### The .env File

The `.env` file contains all your configuration. Here's a complete example:

```env
# ============================================================
# LLM PROVIDER SELECTION
# ============================================================
# Options: openai, anthropic, ollama
LLM_PROVIDER=openai

# ============================================================
# OPENAI CONFIGURATION
# ============================================================
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini

# ============================================================
# ANTHROPIC CONFIGURATION (if using Claude)
# ============================================================
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# ============================================================
# OLLAMA CONFIGURATION (if using local models)
# ============================================================
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# ============================================================
# LANGSMITH TRACING (optional)
# ============================================================
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_xxxxxxxxxxxxxxxxxxxx
LANGCHAIN_PROJECT=multi-agent-research
```

---

## Running the Application

### Basic Usage

```bash
# Interactive mode
python main.py

# Direct query
python main.py "What is machine learning?"

# Show workflow graph
python main.py --show-graph
```

### What You'll See

```
✅ LLM Provider: OPENAI (gpt-4o-mini)
📊 LangSmith tracing ENABLED (Project: multi-agent-research)

    ╔══════════════════════════════════════════════════════════╗
    ║     🔬 Multi-Agent Research Assistant - Interactive      ║
    ╠══════════════════════════════════════════════════════════╣
    ║  Research Commands:                                      ║
    ║    - Type your research topic/question                   ║
    ...

📌 Current Thread: Thread 1 (ID: abc12345...)

[Thread 1] 🔍 Enter topic or command: 
```

---

## LLM Provider Setup

### Option 1: OpenAI (Recommended)

1. Go to https://platform.openai.com/api-keys
2. Create an API key
3. Add to `.env`:
   ```env
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-proj-your-key-here
   OPENAI_MODEL=gpt-4o-mini
   ```

**Available Models:**
- `gpt-4o-mini` - Fast, cheap, good quality (recommended)
- `gpt-4o` - Best quality, more expensive
- `gpt-3.5-turbo` - Fastest, cheapest

### Option 2: Anthropic Claude

1. Go to https://console.anthropic.com/
2. Create an API key
3. Install the package:
   ```bash
   pip install langchain-anthropic
   ```
4. Add to `.env`:
   ```env
   LLM_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ANTHROPIC_MODEL=claude-sonnet-4-20250514
   ```

**Available Models:**
- `claude-sonnet-4-20250514` - Best balance (recommended)
- `claude-opus-4-20250514` - Most capable
- `claude-haiku-4-20250514` - Fastest

### Option 3: Ollama (Free/Local)

1. Install Ollama from https://ollama.ai
2. Start Ollama:
   ```bash
   ollama serve
   ```
3. Pull a model:
   ```bash
   ollama pull llama3.2
   ```
4. Install the package:
   ```bash
   pip install langchain-ollama
   ```
5. Add to `.env`:
   ```env
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2
   ```

**Available Models:**
- `llama3.2` - Meta's latest (recommended)
- `mistral` - Fast and capable
- `codellama` - Good for code
- `mixtral` - Mixture of experts

---

## LangSmith Tracing Setup

LangSmith provides observability for your LLM applications.

### Setup Steps

1. Go to https://smith.langchain.com
2. Create an account
3. Create an API key
4. Add to `.env`:
   ```env
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=lsv2_pt_your-key-here
   LANGCHAIN_PROJECT=multi-agent-research
   ```

### What Tracing Shows

- All LLM calls with inputs/outputs
- Token usage and costs
- Latency metrics
- Agent execution flow
- Error debugging

### Disable Tracing

To disable tracing, set:
```env
LANGCHAIN_TRACING_V2=false
```

---

## Troubleshooting

### Error: "Module not found"

```bash
# Make sure virtual environment is activated
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Error: "OPENAI_API_KEY not found"

1. Check `.env` file exists
2. Check the key is correct (no quotes needed)
3. Check `LLM_PROVIDER` matches your key

```bash
# Verify .env exists
cat .env
```

### Error: "Ollama connection refused"

```bash
# Start Ollama server
ollama serve

# In another terminal, verify it's running
curl http://localhost:11434/api/tags
```

### Error: "Rate limit exceeded"

- OpenAI: Wait a minute and try again, or upgrade your plan
- Anthropic: Same as above
- Ollama: No rate limits (local)

### Error: "charmap codec can't encode"

This is a Windows encoding issue. The project should handle this, but if not:

```bash
# Set UTF-8 encoding in PowerShell
$env:PYTHONIOENCODING="utf-8"

# Or in CMD
set PYTHONIOENCODING=utf-8
```

### Getting Help

If you're still stuck:

1. Check the error message carefully
2. Search for the error in GitHub Issues
3. Create a new Issue with:
   - Your OS (Windows/Mac/Linux)
   - Python version
   - Full error message
   - Steps to reproduce

---

## Next Steps

Once everything is working:

1. **Try a research query**: `python main.py "What is quantum computing?"`
2. **Explore thread management**: Create multiple threads for different topics
3. **Export your research**: Use `db export csv` to save your work
4. **Check LangSmith**: View your traces at https://smith.langchain.com

Happy researching! 🔬
