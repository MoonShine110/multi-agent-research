"""
LLM Provider Module - Flexible LLM Selection

This module provides a unified interface for different LLM providers:
- OpenAI (GPT-4, GPT-4o-mini, etc.)
- Anthropic (Claude)
- Ollama (Local models like Llama, Mistral, etc.)

Usage:
    Set LLM_PROVIDER in .env to: openai, anthropic, or ollama
    Then configure the corresponding API keys/settings
"""

import os
from typing import Optional


def get_llm(temperature: float = 0.3, max_tokens: int = 4096):
    """
    Get the configured LLM based on environment variables.
    
    Args:
        temperature: LLM temperature (0.0-1.0)
        max_tokens: Maximum tokens in response
        
    Returns:
        Configured LLM instance (ChatOpenAI, ChatAnthropic, or ChatOllama)
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "openai":
        return _get_openai_llm(temperature, max_tokens)
    elif provider == "anthropic":
        return _get_anthropic_llm(temperature, max_tokens)
    elif provider == "ollama":
        return _get_ollama_llm(temperature, max_tokens)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}. Use: openai, anthropic, or ollama")


def _get_openai_llm(temperature: float, max_tokens: int):
    """Get OpenAI LLM instance."""
    from langchain_openai import ChatOpenAI
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment. Add it to .env file.")
    
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    print(f"   🤖 Using OpenAI: {model}")
    
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=api_key
    )


def _get_anthropic_llm(temperature: float, max_tokens: int):
    """Get Anthropic Claude LLM instance."""
    try:
        from langchain_anthropic import ChatAnthropic
    except ImportError:
        raise ImportError("Please install langchain-anthropic: pip install langchain-anthropic")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment. Add it to .env file.")
    
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    
    print(f"   🤖 Using Anthropic: {model}")
    
    return ChatAnthropic(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=api_key
    )


def _get_ollama_llm(temperature: float, max_tokens: int):
    """Get Ollama (local) LLM instance."""
    try:
        from langchain_ollama import ChatOllama
    except ImportError:
        raise ImportError("Please install langchain-ollama: pip install langchain-ollama")
    
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    print(f"   🤖 Using Ollama: {model} at {base_url}")
    
    return ChatOllama(
        model=model,
        temperature=temperature,
        base_url=base_url
    )


def get_provider_info() -> dict:
    """Get information about the current LLM provider configuration."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    info = {
        "provider": provider,
        "configured": False,
        "model": None
    }
    
    if provider == "openai":
        info["configured"] = bool(os.getenv("OPENAI_API_KEY"))
        info["model"] = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    elif provider == "anthropic":
        info["configured"] = bool(os.getenv("ANTHROPIC_API_KEY"))
        info["model"] = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    elif provider == "ollama":
        info["configured"] = True  # Ollama doesn't need API key
        info["model"] = os.getenv("OLLAMA_MODEL", "llama3.2")
        info["base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    return info


def validate_provider_config() -> tuple[bool, str]:
    """
    Validate that the LLM provider is properly configured.
    
    Returns:
        Tuple of (is_valid, message)
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            return False, "OPENAI_API_KEY not found. Add it to your .env file."
        return True, f"OpenAI configured with model: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}"
    
    elif provider == "anthropic":
        if not os.getenv("ANTHROPIC_API_KEY"):
            return False, "ANTHROPIC_API_KEY not found. Add it to your .env file."
        return True, f"Anthropic configured with model: {os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')}"
    
    elif provider == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama3.2")
        return True, f"Ollama configured with model: {model} at {base_url}"
    
    else:
        return False, f"Unknown provider: {provider}. Use: openai, anthropic, or ollama"
