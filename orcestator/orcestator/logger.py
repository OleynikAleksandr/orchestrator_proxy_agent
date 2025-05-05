"""
Logging module for Orcestator.
Provides text logging and Prometheus metrics.
"""

import csv
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from prometheus_client import Counter, Gauge, Histogram, start_http_server

from orcestator.config import Config
from orcestator.db import log_request


logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("orcestator")

os.makedirs(os.path.dirname(Config.LOG_FILE), exist_ok=True)

REQUEST_COUNT = Counter(
    "orcestator_requests_total", 
    "Total number of requests processed",
    ["model"]
)
PROMPT_TOKENS = Counter(
    "orcestator_prompt_tokens_total", 
    "Total number of prompt tokens processed",
    ["model"]
)
COMPLETION_TOKENS = Counter(
    "orcestator_completion_tokens_total", 
    "Total number of completion tokens processed",
    ["model"]
)
LATENCY = Histogram(
    "orcestator_request_latency_seconds", 
    "Request latency in seconds",
    ["model"]
)
ACTIVE_REQUESTS = Gauge(
    "orcestator_active_requests", 
    "Number of active requests",
    ["model"]
)


def start_metrics_server(port: int = 8001) -> None:
    """
    Start the Prometheus metrics server.
    
    Args:
        port: Port to run the metrics server on
    """
    start_http_server(port)
    logger.info(f"Prometheus metrics server started on port {port}")


def log_to_file(
    user_message: str,
    assistant_message: str,
    prompt_tokens: int,
    completion_tokens: int,
    latency_ms: int,
    model: str,
    original_model: str = "",
) -> None:
    """
    Log request details to the configured log file.
    
    Args:
        user_message: The user's message
        assistant_message: The assistant's response
        prompt_tokens: Number of tokens in the prompt
        completion_tokens: Number of tokens in the completion
        latency_ms: Latency in milliseconds
        model: The model used (orcestator)
        original_model: The original model used (e.g., openai/gpt-4o)
    """
    timestamp = datetime.utcnow().isoformat()
    
    user_message_short = (user_message[:100] + "...") if len(user_message) > 100 else user_message
    assistant_message_short = (assistant_message[:100] + "...") if len(assistant_message) > 100 else assistant_message
    
    log_entry = [
        timestamp,
        user_message_short.replace("\n", " "),
        assistant_message_short.replace("\n", " "),
        str(prompt_tokens),
        str(completion_tokens),
        str(latency_ms),
        model,
        original_model
    ]
    
    log_file = Path(Config.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    file_exists = log_file.exists()
    
    with open(log_file, "a", newline="") as f:
        writer = csv.writer(f, delimiter="|")
        if not file_exists:
            writer.writerow([
                "timestamp", "user", "assistant", "prompt_tokens", 
                "completion_tokens", "latency_ms", "model", "original_model"
            ])
        writer.writerow(log_entry)
    
    log_request(
        user_message=user_message,
        assistant_message=assistant_message,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        latency_ms=latency_ms,
        model=model,
        original_model=original_model,
    )


def update_metrics(
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    latency_seconds: float,
) -> None:
    """
    Update Prometheus metrics.
    
    Args:
        model: The model used
        prompt_tokens: Number of tokens in the prompt
        completion_tokens: Number of tokens in the completion
        latency_seconds: Latency in seconds
    """
    REQUEST_COUNT.labels(model=model).inc()
    PROMPT_TOKENS.labels(model=model).inc(prompt_tokens)
    COMPLETION_TOKENS.labels(model=model).inc(completion_tokens)
    LATENCY.labels(model=model).observe(latency_seconds)


class RequestTimer:
    """Context manager for timing requests and updating metrics."""
    
    def __init__(self, model: str):
        """
        Initialize the timer.
        
        Args:
            model: The model being used
        """
        self.model = model
        self.start_time = None
        self.latency_seconds = 0
    
    def __enter__(self) -> "RequestTimer":
        """Start the timer and increment active requests."""
        self.start_time = time.time()
        ACTIVE_REQUESTS.labels(model=self.model).inc()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Stop the timer, calculate latency, and decrement active requests.
        
        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        if self.start_time is not None:
            self.latency_seconds = time.time() - self.start_time
            ACTIVE_REQUESTS.labels(model=self.model).dec()
