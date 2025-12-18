"""
Centralized LLM utility using LangChain with OpenRouter
Provides a single LLM instance that can be used across all services
"""
import os
import logging
from typing import Optional
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

class LLMConfig:
    """Configuration for LLM"""
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
    DEFAULT_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    DEFAULT_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "150"))

def get_llm(
    temperature: Optional[float] = None,
    timeout: Optional[int] = None,
    model: Optional[str] = None
) -> ChatOpenAI:
    """
    Get a configured LLM instance using OpenRouter
    
    Args:
        temperature: Temperature for the LLM (default: from config)
        timeout: Timeout in seconds (default: from config)
        model: Model name (default: from config)
        
    Returns:
        Configured ChatOpenAI instance
    """
    if not LLMConfig.OPENROUTER_API_KEY:
        raise ValueError("API Key is not set in environment variables")
    
    
    # Check if we should fallback to Google Direct (User preference or specific AIza key set as OPENROUTER_API_KEY)
    # The .env shows both keys are available. Let's respect the OPENROUTER_API_KEY content.
    if LLMConfig.OPENROUTER_API_KEY.startswith("AIza"):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            logger.info("Detected Google API Key in OPENROUTER_API_KEY. Switching to ChatGoogleGenerativeAI.")
            return ChatGoogleGenerativeAI(
                google_api_key=LLMConfig.OPENROUTER_API_KEY,
                model="gemini-1.5-flash",
                temperature=temperature if temperature is not None else LLMConfig.DEFAULT_TEMPERATURE,
                timeout=timeout if timeout is not None else LLMConfig.DEFAULT_TIMEOUT,
            )
        except ImportError:
            logger.error("langchain-google-genai not installed.")
            raise

    # Standard OpenRouter Configuration
    # Add headers as per documentation to avoid 401s or ranking issues
    headers = {
        "HTTP-Referer": "http://localhost:3000", 
        "X-Title": "BearCart Analytics"
    }

    masked_key = LLMConfig.OPENROUTER_API_KEY[:6] + "..." + LLMConfig.OPENROUTER_API_KEY[-4:]
    logger.info(f"Using OpenRouter with key: {masked_key}")

    llm = ChatOpenAI(
        api_key=LLMConfig.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        model=model or LLMConfig.OPENROUTER_MODEL,
        temperature=temperature if temperature is not None else LLMConfig.DEFAULT_TEMPERATURE,
        timeout=timeout if timeout is not None else LLMConfig.DEFAULT_TIMEOUT,
        default_headers=headers
    )
    
    logger.info(f"Initialized LLM with model: {model or LLMConfig.OPENROUTER_MODEL}, temperature: {temperature or LLMConfig.DEFAULT_TEMPERATURE}")
    
    return llm