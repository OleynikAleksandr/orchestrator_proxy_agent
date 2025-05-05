"""
Custom FastChat worker that proxies requests to OpenRouter.
"""

import argparse
import asyncio
import json
import time
from typing import AsyncGenerator, Dict, List, Optional, Union

import httpx
from fastchat.serve.base_model_worker import BaseModelWorker
from fastchat.serve.model_worker import app
from fastchat.utils import build_logger

from orcestator.config import Config
from orcestator.logger import RequestTimer, log_to_file, update_metrics

logger = build_logger("proxy_worker", "proxy_worker.log")


class ProxyWorker(BaseModelWorker):
    """
    Custom worker that proxies requests to OpenRouter.
    Inherits from FastChat's BaseModelWorker.
    """

    def __init__(
        self,
        controller_addr: str,
        worker_addr: str,
        worker_id: str,
        model_names: List[str],
        limit_worker_concurrency: int,
        no_register: bool,
    ):
        """
        Initialize the proxy worker.
        
        Args:
            controller_addr: Address of the controller
            worker_addr: Address of this worker
            worker_id: ID of this worker
            model_names: List of model names this worker serves
            limit_worker_concurrency: Maximum number of concurrent requests
            no_register: Whether to register with the controller
        """
        super().__init__(
            controller_addr=controller_addr,
            worker_addr=worker_addr,
            worker_id=worker_id,
            model_names=model_names,
            limit_worker_concurrency=limit_worker_concurrency,
            no_register=no_register,
        )
        
        if not Config.API_KEY:
            raise ValueError("OR_API_KEY environment variable is required")
        
        self.client = httpx.AsyncClient(
            base_url="https://openrouter.ai/api/v1",
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {Config.API_KEY}",
                "HTTP-Referer": "https://github.com/OleynikAleksandr/orchestrator_proxy_agent",
                "X-Title": "Orcestator Proxy",
            },
        )
        
        logger.info(f"ProxyWorker initialized with models: {model_names}")

    async def generate_stream(
        self,
        params: Dict,
        **kwargs,
    ) -> AsyncGenerator[Dict, None]:
        """
        Generate a stream of responses by proxying to OpenRouter.
        
        Args:
            params: Parameters for the generation
            
        Yields:
            Dict: Generated responses
        """
        context = params.get("prompt", "")
        temperature = float(params.get("temperature", 1.0))
        top_p = float(params.get("top_p", 1.0))
        max_tokens = params.get("max_new_tokens", 2048)
        echo = params.get("echo", False)
        stop_str = params.get("stop", None)
        stop_token_ids = params.get("stop_token_ids", None)
        
        messages = params.get("messages", [])
        if not messages and context:
            messages = [{"role": "user", "content": context}]
        
        model_name = params.get("model", "orcestator")
        target_model = Config.DEFAULT_MODEL if model_name == "orcestator" else model_name
        
        request_data = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "stream": True,
        }
        
        if stop_str:
            request_data["stop"] = stop_str if isinstance(stop_str, list) else [stop_str]
        
        with RequestTimer(model=model_name) as timer:
            try:
                async with self.client.stream(
                    "POST",
                    "/chat/completions",
                    json=request_data,
                    timeout=60.0,
                ) as response:
                    response.raise_for_status()
                    
                    full_response = ""
                    prompt_tokens = 0
                    completion_tokens = 0
                    
                    async for line in response.aiter_lines():
                        if not line or line.startswith(":"):
                            continue
                        
                        if line.startswith("data: "):
                            line = line[6:]  # Remove "data: " prefix
                        
                        if line.strip() == "[DONE]":
                            break
                        
                        try:
                            chunk = json.loads(line)
                            
                            if "usage" in chunk:
                                usage = chunk["usage"]
                                prompt_tokens = usage.get("prompt_tokens", 0)
                                completion_tokens = usage.get("completion_tokens", 0)
                            
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            
                            if content:
                                full_response += content
                            
                            if "model" in chunk:
                                chunk["model"] = "orcestator"
                            
                            yield {"text": full_response, "error_code": 0}
                        
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse JSON: {line}")
                            continue
                    
                    user_message = messages[0]["content"] if messages else ""
                    latency_ms = int(timer.latency_seconds * 1000)
                    
                    update_metrics(
                        model=model_name,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        latency_seconds=timer.latency_seconds,
                    )
                    
                    log_to_file(
                        user_message=user_message,
                        assistant_message=full_response,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        latency_ms=latency_ms,
                        model=model_name,
                        original_model=target_model,
                    )
            
            except Exception as e:
                logger.error(f"Error in generate_stream: {str(e)}")
                yield {"text": f"Error: {str(e)}", "error_code": 1}

    async def generate(
        self,
        params: Dict,
        **kwargs,
    ) -> Dict:
        """
        Generate a response by proxying to OpenRouter (non-streaming).
        
        Args:
            params: Parameters for the generation
            
        Returns:
            Dict: Generated response
        """
        full_response = ""
        async for chunk in self.generate_stream(params, **kwargs):
            if chunk.get("error_code", 0) == 0:
                full_response = chunk["text"]
        
        return {"text": full_response, "error_code": 0}


def create_worker(args):
    """
    Create and start a proxy worker.
    
    Args:
        args: Command line arguments
    """
    worker = ProxyWorker(
        controller_addr=args.controller_address,
        worker_addr=args.worker_address,
        worker_id=args.worker_id,
        model_names=args.model_names,
        limit_worker_concurrency=args.limit_worker_concurrency,
        no_register=args.no_register,
    )
    return worker


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--controller-address", type=str, default=f"http://localhost:{Config.CONTROLLER_PORT}")
    parser.add_argument("--worker-address", type=str, default=f"http://localhost:{Config.WORKER_PORT}")
    parser.add_argument("--worker-id", type=str, default="proxy-worker")
    parser.add_argument("--model-id", type=str, default="orcestator")
    parser.add_argument("--model-names", type=str, nargs="+", default=None)
    parser.add_argument("--limit-worker-concurrency", type=int, default=5)
    parser.add_argument("--no-register", action="store_true")
    parser.add_argument("--port", type=int, default=Config.WORKER_PORT)
    
    args = parser.parse_args()
    
    if args.model_names is None:
        args.model_names = [args.model_id]
    
    args.worker_address = f"http://localhost:{args.port}"
    
    worker = create_worker(args)
    
    app.title = "Orcestator Proxy Worker"
    uvicorn_kwargs = {
        "host": "0.0.0.0",
        "port": args.port,
        "log_level": "info",
        "timeout_keep_alive": 60,
    }
    
    app.worker = worker
    import uvicorn
    uvicorn.run(app, **uvicorn_kwargs)
