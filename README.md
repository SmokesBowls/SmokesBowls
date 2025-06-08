- 👋 Hi, I’m @SmokesBowls
- 👀 I’m interested in ...learning and creating 
- 🌱 I’m currently learning ...python, pycharm, conda, blender 3d, android studio, vietnamese 
- 💞️ I’m looking to collaborate on ...
- 📫 How to reach me ...

<!---
SmokesBowls/SmokesBowls is a ✨ special ✨ repository because its `README.md` (this file) appears on your GitHub profile.
You can click the Preview link to take a look at your changes.
--->

---

## ZW MCP Server (Ollama Interface)

This project implements a system to send ZW-formatted prompts from files to a local Ollama instance, save Ollama's responses to files, and optionally log interactions.

### Directory Structure

```
zw_mcp/
├── zw_mcp_server.py        # CLI entry point
├── ollama_handler.py       # Handles API requests to Ollama
├── prompts/
│   └── example.zw          # Example ZW input prompt
├── responses/
│   └──                     # Directory for saved Ollama responses
└── logs/
    └──                     # Directory for session logs
```

### Core Scripts

- **`zw_mcp/ollama_handler.py`**: Handles the low-level communication with the Ollama API (`http://localhost:11434/api/generate`).
- **`zw_mcp/zw_mcp_server.py`**: The main command-line interface (CLI) tool. It now supports:
    - Reading ZW-formatted prompts from an input file.
    - Sending the prompt to a local Ollama instance.
    - Printing Ollama's response to the console.
    - Optionally saving Ollama's response to an output file.
    - Optionally logging the prompt and response to a log file.

### Prerequisites

- Python 3
- `requests` library (`pip install requests`)
- A running local Ollama instance.

### Usage

The `zw_mcp_server.py` script is run from the root directory of the repository.

**Command-line arguments:**

```
usage: zw_mcp_server.py [-h] [--out OUT] [--log LOG] infile

ZW MCP ↔ Ollama

positional arguments:
  infile      Path to .zw input file (e.g., zw_mcp/prompts/example.zw)

options:
  -h, --help  show this help message and exit
  --out OUT   Path to save Ollama response (e.g., zw_mcp/responses/ollama_response.zw)
  --log LOG   Optional log file (e.g., zw_mcp/logs/session.log)
```

**Example:**

1.  **Ensure you have an input file**, for example, `zw_mcp/prompts/example.zw` with content like:
    ```
    ZW-NARRATIVE-EVENT:
      TITLE: The Awakening
      DIALOGUE:
        - SPEAKER: Tran
          LINE: “This place... I’ve been here before.”
      SCENE_GOAL: Uncover ancient resonance
    ```

2.  **Run the CLI tool from the repository root:**
    To process an input file, save the response, and log the interaction:
    ```bash
    python3 zw_mcp/zw_mcp_server.py zw_mcp/prompts/example.zw --out zw_mcp/responses/response_001.zw --log zw_mcp/logs/session.log
    ```

    - This will read `zw_mcp/prompts/example.zw`.
    - Send its content to Ollama.
    - Print Ollama's response to the console.
    - Save Ollama's response to `zw_mcp/responses/response_001.zw`.
    - Append the prompt and response to `zw_mcp/logs/session.log`.

    To simply process an input file and print to console:
    ```bash
    python3 zw_mcp/zw_mcp_server.py zw_mcp/prompts/example.zw
    ```

3.  The script will indicate that it's sending the prompt to Ollama and then print the response. If output or log paths are specified, it will also confirm saving/logging.
```

---

## Phase 2: TCP Daemon Server (Networked ZW MCP)

This phase transforms the ZW MCP into a network-accessible service, allowing other tools and applications to interact with it over TCP.

### New Scripts for Phase 2

- **`zw_mcp/zw_mcp_daemon.py`**:
    - A TCP server that listens for incoming ZW-formatted prompts on a configurable host and port (default: `127.0.0.1:7421`).
    - Handles multiple client connections concurrently using threading.
    - Receives multi-line ZW input (terminated by `///`).
    - Uses `ollama_handler.py` to query the Ollama API.
    - Sends Ollama's response back to the connected client.
    - Logs all incoming prompts and their corresponding responses to `zw_mcp/logs/daemon.log`.
    - Includes error handling for network operations and graceful shutdown.

- **`zw_mcp/client_example.py`**:
    - An example CLI client to test and interact with the `zw_mcp_daemon.py`.
    - Connects to the daemon at a specified host and port.
    - Reads a ZW-formatted prompt from a local file (e.g., `zw_mcp/prompts/example.zw`).
    - Sends the prompt to the daemon.
    - Receives the daemon's response (from Ollama) and prints it to the console.
    - Includes error handling for file and network operations.

### How to Use the TCP Daemon

1.  **Start the ZW MCP Daemon:**
    Open a terminal and run the daemon script. It's recommended to run it from the root of the repository.
    ```bash
    python3 zw_mcp/zw_mcp_daemon.py
    ```
    The daemon will print a message indicating it's listening, e.g., `🌐 ZW MCP Daemon listening on 127.0.0.1:7421 ...`
    All interactions will be logged to `zw_mcp/logs/daemon.log`.

2.  **Run the Example Client (or your own tool):**
    Open another terminal and run the client script.
    To send the default prompt (`zw_mcp/prompts/example.zw`):
    ```bash
    python3 zw_mcp/client_example.py
    ```
    To send a specific prompt file:
    ```bash
    python3 zw_mcp/client_example.py path/to/your/prompt.zw
    ```
    The client will print the response received from the daemon.

### Capabilities Unlocked

This networked setup allows various external applications to interface with the ZW MCP and, by extension, with Ollama. This could include:
- GUIs or web frontends for ZW interaction.
- Integration with other creative tools (e.g., Blender scripts).
- Communication between different AI agents or systems.

### Directory Structure (Updated for Phase 2)

The directory structure remains largely the same, with the addition of the new daemon and client scripts within `zw_mcp/`:
```
zw_mcp/
├── zw_mcp_daemon.py        # NEW: TCP Daemon server
├── client_example.py       # NEW: Example TCP client
├── zw_mcp_server.py        # CLI tool (from Phase 1.5)
├── ollama_handler.py       # Handles API requests to Ollama
├── prompts/
│   └── example.zw          # Example ZW input prompt
├── responses/
│   └──                     # Directory for saved CLI responses
└── logs/
    ├── daemon.log          # NEW: Log for TCP daemon interactions
    └── session.log         # Log for CLI tool interactions (from Phase 1.5)
```
Note: The `responses/` directory is primarily used by the CLI tool (`zw_mcp_server.py`). The daemon sends responses directly back to the client.
```
