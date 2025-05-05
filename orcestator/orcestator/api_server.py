"""
Wrapper for FastChat's OpenAI API server.
Adds the 'orcestator' model to the available models.
"""

import argparse
import sys
from typing import Dict, List

from fastchat.serve.openai_api_server import app, build_logger, create_app, get_model_list
from fastchat.utils import str_to_bool

from orcestator.config import Config
from orcestator.logger import start_metrics_server

logger = build_logger("api_server", "api_server.log")


def patch_model_list(model_list: List[Dict]) -> List[Dict]:
    """
    Add the 'orcestator' model to the model list.
    
    Args:
        model_list: Original model list from FastChat
        
    Returns:
        List[Dict]: Updated model list with 'orcestator' added
    """
    for model in model_list:
        if model["id"] == "orcestator":
            return model_list
    
    orcestator_model = {
        "id": "orcestator",
        "object": "model",
        "created": 1677610602,
        "owned_by": "orcestator",
        "permission": [],
        "root": "orcestator",
        "parent": None,
    }
    
    model_list.append(orcestator_model)
    return model_list


original_get_model_list = get_model_list

def patched_get_model_list(*args, **kwargs):
    """
    Patched version of get_model_list that adds 'orcestator' to the model list.
    """
    model_list = original_get_model_list(*args, **kwargs)
    return patch_model_list(model_list)


get_model_list = patched_get_model_list


def run_api_server():
    """
    Run the OpenAI API server with the 'orcestator' model added.
    """
    if not Config.validate():
        sys.exit(1)
    
    start_metrics_server()
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default=Config.HOST)
    parser.add_argument("--port", type=int, default=Config.PORT)
    parser.add_argument("--controller-address", type=str, default=f"http://localhost:{Config.CONTROLLER_PORT}")
    parser.add_argument("--allow-credentials", type=str_to_bool, default=True)
    parser.add_argument("--allowed-origins", type=str, default="*")
    parser.add_argument("--allowed-methods", type=str, default="*")
    parser.add_argument("--allowed-headers", type=str, default="*")
    parser.add_argument("--api-keys", type=str)
    
    args = parser.parse_args()
    
    logger.info(f"Starting Orcestator API server at {args.host}:{args.port}")
    logger.info(f"Using controller at {args.controller_address}")
    
    create_app(args)
    
    import uvicorn
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    run_api_server()
