import json
import os
import importlib
from typing import Optional, Tuple, Dict, List


def load_agents_config(path: str = "config/agents_config.json") -> Dict:
    """
    Loads the JSON configuration file for agents.

    Args:
        path (str): Path to the JSON file.

    Returns:
        Dict: Dictionary containing the agents configuration.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Configuration file not found at: {path}")
        return {"agents": []}
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {path}: {e}")
        return {"agents": []}


def get_agent_names(agent_config: Dict) -> List[str]:
    """
    Extracts the names of available agents.

    Args:
        agent_config (Dict): Full loaded configuration.

    Returns:
        List[str]: List of agent names.
    """
    return [agent["name"] for agent in agent_config.get("agents", [])]


def get_agent_info(agent_config: Dict, name: str) -> Optional[Dict]:
    """
    Retrieves metadata of an agent by name.

    Args:
        agent_config (Dict): Full configuration.
        name (str): Name of the agent to search for.

    Returns:
        Optional[Dict]: Agent information or None if not found.
    """
    return next((agent for agent in agent_config.get("agents", []) if agent["name"] == name), None)


def check_required_apis(agent_info: Dict, api_keys: Dict[str, str]) -> List[str]:
    """
    Checks which API keys are missing for an agent.

    Args:
        agent_info (Dict): Information about the selected agent.
        api_keys (Dict): Available API keys.

    Returns:
        List[str]: List of missing API keys.
    """
    required = agent_info.get("requires", [])
    if isinstance(required, str):
        required = [required]

    return [api for api in required if not api_keys.get(api)]


def load_agent_instance(agent_info: Dict, api_keys: Dict[str, str]):
    """
    Dynamically instantiates an agent class from its configuration.

    Args:
        agent_info (Dict): Agent configuration.
        api_keys (Dict): API keys to inject into environment variables.

    Returns:
        instance: Instance of the agent class.
    """
    # Set environment variables from API keys
    for key, value in api_keys.items():
        if value:
            os.environ[key.upper()] = value

    # Dynamic import
    module = importlib.import_module(agent_info["module_path"])
    agent_class = getattr(module, agent_info["class_name"])

    return agent_class()
