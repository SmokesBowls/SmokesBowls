import os
import requests
from typing import List, Dict, Any, Optional

# Allow override; default to the healthy port you verified
OLLAMA_BASE = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

# Endpoints
GEN_URL  = f"{OLLAMA_BASE}/api/generate"  # one-shot prompt
CHAT_URL = f"{OLLAMA_BASE}/api/chat"      # multi-turn messages

# Default model (keep small for 1050 Ti)
DEFAULT_MODEL = os.getenv("ZW_MCP_MODEL", "llama3.2")

def _post(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    print(f"[OLLAMA] POST {url} :: {payload.get('model')}", flush=True)
    r = requests.post(url, json=payload, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"Ollama error {r.status_code}: {r.text[:800]}")
    return r.json()

def generate(prompt: str, model: Optional[str] = None, stream: bool = False) -> Dict[str, Any]:
    payload = {
        "model": model or DEFAULT_MODEL,
        "prompt": prompt,
        "stream": stream,
    }
    return _post(GEN_URL, payload)

def chat(messages: List[Dict[str, str]], model: Optional[str] = None, stream: bool = False) -> Dict[str, Any]:
    # messages like: [{"role":"user","content":"..."}]
    payload = {
        "model": model or DEFAULT_MODEL,
        "messages": messages,
        "stream": stream,
    }
    return _post(CHAT_URL, payload)

# What the daemon imports
def query_ollama(prompt: str, model: Optional[str] = None) -> str:
    data = generate(prompt, model=model, stream=False)
    # /api/generate returns {"response": "...", ...}
    return data.get("response", "")
