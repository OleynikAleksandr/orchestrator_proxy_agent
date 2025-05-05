"""
Database module for Orcestator.
Provides SQLModel models for request logging if OR_DB_PATH is set.
"""

import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, create_engine, Session

from orcestator.config import Config


class RequestLog(SQLModel, table=True):
    """Model for logging API requests and responses."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    user_message: str = Field(index=True)
    assistant_message: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int
    model: str = Field(index=True)
    original_model: str = Field(default="")


engine = None
if Config.DB_PATH:
    engine = create_engine(f"sqlite:///{Config.DB_PATH}", echo=False)
    SQLModel.metadata.create_all(engine)


def log_request(
    user_message: str,
    assistant_message: str,
    prompt_tokens: int,
    completion_tokens: int,
    latency_ms: int,
    model: str,
    original_model: str = "",
) -> None:
    """
    Log a request to the database if DB_PATH is set.
    
    Args:
        user_message: The user's message
        assistant_message: The assistant's response
        prompt_tokens: Number of tokens in the prompt
        completion_tokens: Number of tokens in the completion
        latency_ms: Latency in milliseconds
        model: The model used (orcestator)
        original_model: The original model used (e.g., openai/gpt-4o)
    """
    if not engine:
        return
    
    log_entry = RequestLog(
        user_message=user_message,
        assistant_message=assistant_message,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        latency_ms=latency_ms,
        model=model,
        original_model=original_model,
    )
    
    with Session(engine) as session:
        session.add(log_entry)
        session.commit()
