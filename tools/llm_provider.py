"""
LLM Provider Module - Flexible LLM Selection

Supports multiple LLM providers:
- OpenAI (GPT-4o-mini, GPT-4o, etc.)
- Anthropic (Claude Sonnet, Claude Opus, etc.)
- Ollama (Llama, Mistral, etc. - local/free)

Configure in .env file:
    LLM_PROVIDER=openai|anthropic|ollama
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_llm(temperature: float = 0.3, max_tokens: int = 4096):
    """
    Get the configured LLM based on environment variables.
    
    Reads LLM_PROVIDER from .env and returns the appropriate LLM.
    
    Args:
        temperature: LLM temperature (0.0-1.0)
        max_tokens: Maximum tokens in response
        
    Returns:
        Configured LLM instance
        
    Raises:
        ValueError: If provider is not supported or API key missing
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "openai":
        return _get_openai_llm(temperature, max_tokens)
    elif provider == "anthropic":
        return _get_anthropic_llm(temperature, max_tokens)
    elif provider == "ollama":
        return _get_ollama_llm(temperature, max_tokens)
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER: {provider}. "
            "Supported: openai, anthropic, ollama"
        )


def _get_openai_llm(temperature: float, max_tokens: int):
    """Get OpenAI LLM instance."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or api_key == "sk-your-openai-key-here":
        raise ValueError(
            "OPENAI_API_KEY not configured. "
            "Please set it in your .env file."
        )
    
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        raise ImportError(
            "langchain-openai not installed. "
            "Run: pip install langchain-openai"
        )
    
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    print(f"🤖 Using OpenAI: {model}")
    
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=api_key
    )


def _get_anthropic_llm(temperature: float, max_tokens: int):
    """Get Anthropic/Claude LLM instance."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key or api_key == "sk-ant-your-anthropic-key-here":
        raise ValueError(
            "ANTHROPIC_API_KEY not configured. "
            "Please set it in your .env file."
        )
    
    try:
        from langchain_anthropic import ChatAnthropic
    except ImportError:
        raise ImportError(
            "langchain-anthropic not installed. "
            "Run: pip install langchain-anthropic"
        )
    
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    
    print(f"🤖 Using Anthropic: {model}")
    
    return ChatAnthropic(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=api_key
    )


def _get_ollama_llm(temperature: float, max_tokens: int):
    """Get Ollama LLM instance (local/free)."""
    try:
        from langchain_ollama import ChatOllama
    except ImportError:
        # Fallback to community version
        try:
            from langchain_community.chat_models import ChatOllama
        except ImportError:
            raise ImportError(
                "langchain-ollama not installed. "
                "Run: pip install langchain-ollama"
            )
    
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    print(f"🤖 Using Ollama: {model} at {base_url}")
    
    return ChatOllama(
        model=model,
        temperature=temperature,
        base_url=base_url,
        # Note: Ollama doesn't support max_tokens in the same way
    )


def get_provider_info() -> dict:
    """Get information about the configured LLM provider."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    info = {
        "provider": provider,
        "configured": False,
        "model": None
    }
    
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
        info["configured"] = bool(api_key) and api_key != "sk-your-openai-key-here"
        info["model"] = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        info["configured"] = bool(api_key) and api_key != "sk-ant-your-anthropic-key-here"
        info["model"] = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        
    elif provider == "ollama":
        info["configured"] = True  # Ollama doesn't need API key
        info["model"] = os.getenv("OLLAMA_MODEL", "llama3.2")
        info["base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    return info


def validate_provider() -> tuple[bool, str]:
    """
    Validate that the configured LLM provider is ready to use.
    
    Returns:
        Tuple of (is_valid, message)
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key or api_key == "sk-your-openai-key-here":
            return False, "OPENAI_API_KEY not set. Please configure in .env"
        return True, f"OpenAI configured with {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}"
    
    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key or api_key == "sk-ant-your-anthropic-key-here":
            return False, "ANTHROPIC_API_KEY not set. Please configure in .env"
        return True, f"Anthropic configured with {os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')}"
    
    elif provider == "ollama":
        # Check if Ollama is running
        import urllib.request
        try:
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            urllib.request.urlopen(f"{base_url}/api/tags", timeout=2)
            return True, f"Ollama configured with {os.getenv('OLLAMA_MODEL', 'llama3.2')}"
        except:
            return False, "Ollama not running. Start with: ollama serve"
    
    return False, f"Unknown provider: {provider}"
