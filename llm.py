import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from daily_paper_agent.config import (
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    SiliconCloud_API_KEY,
    SiliconCloud_MODEL,
    VERTEX_PROJECT,
    VERTEX_LOCATION,
    VERTEX_MODEL,
)

def get_llm(provider: str = None):
    provider_to_use = provider or LLM_PROVIDER
    if provider_to_use == "openai":
        return ChatOpenAI(
            model=OPENAI_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.3
        )
    elif provider_to_use == "siliconCloud":
        # SiliconCloud often follows OpenAI API format
        return ChatOpenAI(
            model=SiliconCloud_MODEL,
            api_key=SiliconCloud_API_KEY,
            base_url="https://api.siliconflow.cn/v1",
            temperature=0.3
        )
    elif provider_to_use == "gemini":
        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            google_api_key=GEMINI_API_KEY,
            temperature=0.3
        )
    elif provider_to_use == "vertex":
        # Use ChatGoogleGenerativeAI with project/location for Vertex AI
        return ChatGoogleGenerativeAI(
            model=VERTEX_MODEL,
            project=VERTEX_PROJECT,
            location=VERTEX_LOCATION,
            temperature=0.3
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_to_use}")
