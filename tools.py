from ddgs import DDGS
from livekit.agents import RunContext, function_tool
import smtplib
import requests
import logging
from markdown_pdf import MarkdownPdf
import os
from mem0 import Memory
from config import userID
from pydantic import BaseModel, ConfigDict
from typing import Optional

from datetime import datetime, timezone 
logging.basicConfig(filename="agent.log", filemode="w",
                    format="%(name)s → %(levelname)s: %(message)s")


logging.getLogger("opentelemetry").setLevel(logging.CRITICAL)

class MemoryMetadata(BaseModel):
    category: str                         
    source: str | None = None             
    created_at: datetime | None = None    
    system_generated: bool | None = None  
    model_config = ConfigDict(extra="forbid")

class SaveToMemoryParams(BaseModel):
    text: str
    metadata: MemoryMetadata
    ID: Optional[str] = None
    model_config = ConfigDict(extra="forbid")

os.makedirs("/workspaces/Kyle_AI_Voice_Assistant_RT/dbs", exist_ok=True)
os.makedirs("/workspaces/Kyle_AI_Voice_Assistant_RT/dbs/vector", exist_ok=True)
os.makedirs("/workspaces/Kyle_AI_Voice_Assistant_RT/dbs/history", exist_ok=True)


config = {
    "llm": {
        "provider": "groq",
        "config": {
            "model": "llama-3.1-8b-instant",
            "temperature": 0.1,
            "max_tokens": 2000,
        }
    },
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "multi-qa-MiniLM-L6-cos-v1"
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "memories",
            "path": "/workspaces/Kyle_AI_Voice_Assistant_RT/dbs/vector/",
            "embedding_model_dims": 384,
            "on_disk": True
        }
    },
    "history_db_path": "/workspaces/Kyle_AI_Voice_Assistant_RT/dbs/history/history.sqlite",
    "custom_update_memory_prompt": """
You are a memory manager. When new facts contradict existing memories, DELETE the old memory and ADD the new one.

Rules:
- If user's name changes (e.g., "John" to "Jose"), DELETE the old name memory and ADD the new name.
- Never keep contradicting information about the same attribute (name, location, preferences).
- For updates to the same fact, use DELETE on old + ADD for new.

Return actions: ADD, UPDATE, DELETE, or NONE for each memory.""",
    "version": "v1.1"
}

m = Memory.from_config(config_dict=config)

@function_tool()
async def write_memory(context: RunContext, params: SaveToMemoryParams) -> str:
    """Saves text to memory with metadata."""
    try:
        # Provide more context for the LLM to extract facts
        content = f"My name is {params.text}" if params.metadata.category == "user_info" else params.text
        
        result = m.add(
            messages=[{"role": "user", "content": content}],
            user_id=userID,
            metadata=params.metadata.model_dump(),
        )
        
        if result.get("results"):
            return f"Memory saved: {result['results']}"
        return "Memory processed."
        
    except Exception as e:
        logging.exception("Error in write_memory")
        return "Error saving to memory."


@function_tool()
async def read_memory(context: RunContext, query: str, category: str = None) -> str:
    """Retrieves memories matching the query."""
    try:
        # OSS uses user_id as direct parameter, not in filters
        results = m.search(
            query=query,
            user_id=userID,
            limit=5
        )
        
        if results and results.get("results"):
            memories = [r["memory"] for r in results["results"]]
            return f"Found memories: {memories}"
        return "No memories found."
        
    except Exception as e:
        logging.exception("Error in read_memory")
        return "Error retrieving from memory."








@function_tool()
async def web_search(
        context: RunContext,
        query: str, ) -> str:
    """Searches the internet and retrtives results.
    Args:
        query (str): The search query.
    """
    try:
        if query:
            results = DDGS().text(query, max_results=1)
            
            logging.info(f"Web search results for {query}: {results}")
            return f"Web search results: {results}"
        else:
            return "INVALID QUERY"
    except Exception as e:
        logging.error(f"Error during web search: {e}")
        return "ERROR OCCURED DURING SEARCH"


@function_tool()
async def send_email(
    context: RunContext,
    recipient: str,
    subject: str,
    body: str,
) -> str:
    """Send an email to a given recipient.
    Args:
        recipient (str): The email address of the recipient.
        subject (str): The subject of the email.
        body (str): The body of the email.
    """
    try:
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")

        if not all([smtp_server, smtp_user, smtp_password]):
            return "Email settings are not configured."

        message = (
            f"From: {smtp_user}\n"
            f"To: {recipient}\n"
            f"Subject: {subject}\n\n"
            f"{body}"
        )

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, recipient, message)

        return f"Email sent to {recipient} successfully."

    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return "Sorry, I couldn't send the email right now."

