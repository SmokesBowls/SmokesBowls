# zw_mcp/ollama_agent.py
import socket
import json
from pathlib import Path
from datetime import datetime # Added for logging timestamp

CONFIG_PATH = Path("zw_mcp/agent_config.json")
BUFFER_SIZE = 4096 # Consistent with client_example and daemon

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[!] Error: Agent configuration file not found at '{CONFIG_PATH}'")
        raise
    except json.JSONDecodeError:
        print(f"[!] Error: Could not decode JSON from '{CONFIG_PATH}'")
        raise
    except Exception as e:
        print(f"[!] Error loading agent configuration: {e}")
        raise

def load_prompt(path_str: str) -> str:
    prompt_path = Path(path_str)
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            text = f.read().strip()
            if not text.endswith("///"):
                text += "\n///"
            return text
    except FileNotFoundError:
        print(f"[!] Error: Prompt file not found at '{prompt_path}'")
        raise
    except Exception as e:
        print(f"[!] Error loading prompt file '{prompt_path}': {e}")
        raise

def send_to_daemon(host: str, port: int, prompt: str) -> str:
    print(f"[*] Connecting to ZW MCP Daemon at {host}:{port}...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            print(f"[*] Connected. Sending prompt...")
            s.sendall(prompt.encode("utf-8"))
            s.shutdown(socket.SHUT_WR) # Signal that sending is done

            response_parts = []
            while True:
                try:
                    chunk = s.recv(BUFFER_SIZE)
                    if not chunk:
                        break
                    response_parts.append(chunk.decode("utf-8"))
                except socket.timeout:
                    print("[!] Socket timeout waiting for response.")
                    break
                except Exception as e:
                    print(f"[!] Error receiving response chunk: {e}")
                    break

            if not response_parts:
                print("[!] No response received from server.")
                return "ERROR: No response received from server"

            return "".join(response_parts)

    except socket.error as e:
        print(f"[!] Socket error while communicating with daemon: {e}")
        return f"ERROR: Socket error communicating with daemon - {e}"
    except Exception as e:
        print(f"[!] An unexpected error occurred while communicating with daemon: {e}")
        return f"ERROR: Unexpected error communicating with daemon - {e}"

def log_interaction(log_path_str: str, prompt: str, response: str):
    if not log_path_str:
        print("[*] Log path not configured. Skipping logging.")
        return

    log_file = Path(log_path_str)
    log_file.parent.mkdir(parents=True, exist_ok=True) # Ensure log directory exists

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"--- Prompt [{timestamp}] ---\n{prompt}\n"
    log_entry += f"--- Response [{timestamp}] ---\n{response}\n---\n"

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"[*] Interaction logged to '{log_file.resolve()}'")
    except Exception as e:
        print(f"[!] Error writing to log file '{log_file}': {e}")

def main():
    try:
        config = load_config()
        prompt_text = load_prompt(config["prompt_path"])
    except Exception:
        # Errors already printed by helper functions
        print("[!] Agent cannot continue due to configuration or prompt loading errors.")
        return

    response_text = send_to_daemon(config["host"], config["port"], prompt_text)

    print("\n🧠 ZW Agent Response:\n")
    print(response_text)

    if config.get("log_path"):
        log_interaction(config["log_path"], prompt_text, response_text)
    else:
        print("[*] Logging skipped as 'log_path' not in config.")

if __name__ == "__main__":
    main()
