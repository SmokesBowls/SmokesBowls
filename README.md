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

---

## Phase 2.5: ZW Autonomous Agent (Step 2: Looping Agent with Memory)

This phase enhances the autonomous agent with conversational looping, response chaining, stop-word detection, and persistent memory.

### Agent Files & Configuration

- **`zw_mcp/agent_config.json`**:
    - A JSON configuration file that controls the agent's behavior.
    - **Example Content (Updated for Step 2):**
      ```json
      {
        "prompt_path": "zw_mcp/prompts/example.zw",
        "host": "127.0.0.1",
        "port": 7421,
        "max_rounds": 5,
        "stop_keywords": ["END_SCENE", "///"],
        "log_path": "zw_mcp/logs/agent.log",
        "memory_enabled": true,
        "memory_path": "zw_mcp/logs/memory.json",
        "prepend_previous_response": true
      }
      ```
    - Key settings for Step 2:
        - `prompt_path`: Path to the **initial** ZW prompt file for the first round.
        - `host`, `port`: Network details for the ZW MCP Daemon.
        - `max_rounds`: Maximum number of conversational rounds the agent will perform.
        - `stop_keywords`: A list of strings. If any of these are found in Ollama's response, the agent will stop looping.
        - `log_path`: File path for logging each round's prompt and response (e.g., `zw_mcp/logs/agent.log`).
        - `memory_enabled`: If `true`, the agent saves the prompt and response of each round to a JSON list in `memory_path`.
        - `memory_path`: Path to the JSON file where conversational memory is stored (e.g., `zw_mcp/logs/memory.json`).
        - `prepend_previous_response`: If `true`, the response from the previous round becomes the prompt for the next round (with `///` appended). If `false`, the agent reuses the original `prompt_path` content for each round.


- **`zw_mcp/ollama_agent.py` (Looping Version)**:
    - The Python script for the autonomous agent, now with iterative capabilities.
    - Reads its operational parameters from `zw_mcp/agent_config.json`.
    - **Looping Behavior:**
        - Initiates with the prompt from `prompt_path`.
        - For up to `max_rounds`:
            1. Sends the current prompt to `zw_mcp_daemon.py`.
            2. Receives and prints the response.
            3. Logs the current round's prompt and response to `log_path`.
            4. If `memory_enabled` is true, appends the current round's prompt and response to the list in `memory_path`.
            5. Checks the response for any `stop_keywords`. If found, terminates the loop.
            6. If `prepend_previous_response` is true, the current response (stripped, with `///` appended) becomes the prompt for the next round. Otherwise, the initial prompt from `prompt_path` is used for the next round.
    - Includes error handling for file operations, configuration loading, and network communication.

### How to Use the Looping Agent

1.  **Ensure the ZW MCP Daemon is running:**
    If not already running, start it in a separate terminal:
    ```bash
    python3 zw_mcp/zw_mcp_daemon.py
    ```

2.  **Configure the Agent:**
    Review and edit `zw_mcp/agent_config.json` to set parameters like `prompt_path`, `max_rounds`, `stop_keywords`, `memory_enabled`, `memory_path`, etc., according to your needs.

3.  **Run the Autonomous Agent:**
    In another terminal, execute the agent script:
    ```bash
    python3 zw_mcp/ollama_agent.py
    ```

4.  **Expected Output & Behavior:**
    - The agent will print status messages for each round (e.g., "🔁 Round 1 of 5").
    - The response from Ollama for each round will be printed to the console.
    - The agent will continue for `max_rounds` unless a stop keyword is detected in a response or an error occurs.
    - Each round's prompt and response will be appended to the log file specified in `log_path` (e.g., `zw_mcp/logs/agent.log`).
    - If `memory_enabled` is true, a JSON file (e.g., `zw_mcp/logs/memory.json`) will be created/updated, containing a list of all prompt/response pairs from the session.

### Directory Structure (Updated for Looping Agent)

```
zw_mcp/
├── agent_config.json       # Configuration for the agent
├── ollama_agent.py         # Looping autonomous agent script
├── zw_mcp_daemon.py        # TCP Daemon server
├── client_example.py       # Example TCP client
├── zw_mcp_server.py        # CLI tool
├── ollama_handler.py       # Handles API requests to Ollama
├── prompts/
│   └── example.zw          # Example ZW input prompt
├── responses/
│   └──                     # Directory for saved CLI responses
└── logs/
    ├── agent.log           # Log for autonomous agent interactions (rounds)
    ├── daemon.log          # Log for TCP daemon interactions
    ├── memory.json         # NEW (if memory_enabled): Persistent memory of agent rounds
    └── session.log         # Log for CLI tool interactions
```

This looping agent with memory provides a more powerful way to conduct extended, evolving interactions with Ollama.
```

---
## Phase 2.6: Memory-Driven Agent Personality

This step further refines the ZW Autonomous Agent by allowing its initial prompt to be dynamically constructed based on a defined **style** and a **seed of recent memories**. This gives the agent a configurable persona and immediate historical context for the start of its conversation.

#### Key Functional Changes in `ollama_agent.py` for Personality:

- **Composite Initial Prompt:** If `use_memory_seed` is enabled in `agent_config.json`, the agent no longer uses the `prompt_path` content directly as the first prompt. Instead, it calls a new internal function, `build_composite_prompt()`.
- **`build_composite_prompt()` Function:**
    - Takes the original seed prompt (from `prompt_path`), the `memory_path`, `memory_limit`, and `style` string from the configuration.
    - Constructs a new initial prompt by prepending:
        1.  A `ZW-AGENT-STYLE` block containing the `style` text.
        2.  A `ZW-MEMORY-SEED` block containing a concatenation of the most recent responses from memory (up to `memory_limit`).
    - The original seed prompt is appended after these blocks.
    - This composite prompt is then used for the **first round** of the agent's conversation.
- **Subsequent Rounds:** The logic for subsequent rounds (i.e., how `current_prompt` is updated based on `prepend_previous_response`) remains the same as in Step 2. The personality and memory seeding only affect the very first prompt of a session.

#### New Configuration Fields in `agent_config.json` for Personality:

- **`"style": "You are a prophetic narrator, speaking only in structured ZW format."`**
  - A string that defines the persona, role, or specific instructions for the agent. This is injected into the initial prompt.
- **`"use_memory_seed": true`**
  - A boolean. If `true`, the agent will use the `build_composite_prompt()` logic to prepend style and recent memories to the initial seed prompt. If `false`, the agent uses the `prompt_path` content directly as the initial prompt (as in Step 2 before this change).
- **`"memory_limit": 3`**
  - An integer specifying how many of the most recent entries from `memory.json` should be included in the `ZW-MEMORY-SEED` block when `use_memory_seed` is true.

#### Updated `agent_config.json` Example (Showing All Fields):
```json
{
  "prompt_path": "zw_mcp/prompts/example.zw",
  "host": "127.0.0.1",
  "port": 7421,
  "max_rounds": 5,
  "stop_keywords": ["END_SCENE", "///"],
  "log_path": "zw_mcp/logs/agent.log",
  "memory_enabled": true,
  "memory_path": "zw_mcp/logs/memory.json",
  "prepend_previous_response": true,
  "style": "You are a prophetic narrator, speaking only in structured ZW format.",
  "use_memory_seed": true,
  "memory_limit": 3
}
```

#### How to Use the Agent with Personality:

1.  **Ensure the ZW MCP Daemon is running** (as per previous steps).
2.  **Configure the Agent:**
    - Edit `zw_mcp/agent_config.json`. Pay special attention to `style`, `use_memory_seed`, and `memory_limit` to control the initial prompt's personality.
    - Ensure `memory_path` points to a valid memory file if `use_memory_seed` is true and you expect past memories to be loaded.
3.  **Run the Autonomous Agent:**
    ```bash
    python3 zw_mcp/ollama_agent.py
    ```
4.  **Expected Output & Behavior:**
    - If `use_memory_seed` is true, the **very first prompt** sent to Ollama (and logged in `agent.log`) will be a composite prompt including the style directive, recent memory responses, and the original seed prompt.
    - Subsequent prompts within the same session follow the `prepend_previous_response` logic as before.
    - Ollama's responses should ideally reflect the injected style and be influenced by the seeded memories.
    - All other logging (`agent.log`, `memory.json`) and loop behaviors (`max_rounds`, `stop_keywords`) remain as in Step 2.

This memory-driven personality makes the agent's initial interaction more contextually aware and stylistically aligned, setting a better stage for the ensuing conversation.
```

---
## Phase 3: ZW Parser + Validator

This phase introduces a foundational module, `zw_mcp/zw_parser.py`, designed to parse, validate, and manipulate ZW-formatted text. This utility is crucial for ensuring data integrity, transforming ZW content for different uses, and aiding in debugging.

### Module: `zw_mcp/zw_parser.py`

This module provides a set of functions to work with ZW-formatted text programmatically.

#### Key Functions:

-   **`parse_zw(zw_text: str) -> dict`**
    -   **Purpose:** Converts a string of ZW-formatted text into a nested Python dictionary.
    -   **Details:** Handles indentation to create the nested structure. Lines starting with `#` (comments) or empty lines are ignored. Keys and values are separated by the first colon. A key with no value after the colon (e.g., `PARENT:`) is treated as a parent for a new nested dictionary. List items (e.g., `- ITEM_KEY: ITEM_VAL`) are parsed with the hyphenated part as the literal key.
    -   **Returns:** A dictionary representing the ZW structure.

-   **`to_zw(d: dict, current_indent_level: int = 0) -> str`**
    -   **Purpose:** Converts a nested Python dictionary back into a ZW-formatted text string.
    -   **Details:** Recursively traverses the dictionary, applying indentation (2 spaces per level by default) to reconstruct the ZW hierarchy.
    -   **Returns:** A string in ZW format.

-   **`validate_zw(zw_text: str) -> bool`**
    -   **Purpose:** Performs a basic structural validation of ZW-formatted text.
    -   **Details:** Attempts to parse the text using `parse_zw()`. If parsing is successful and results in a non-empty dictionary, it's considered structurally valid.
    -   **Returns:** `True` if the text appears valid, `False` otherwise (e.g., if parsing raises an error).

-   **`prettify_zw(zw_text: str) -> str`**
    -   **Purpose:** Cleans up and standardizes the formatting of ZW text.
    -   **Details:** Parses the input ZW text into a dictionary using `parse_zw()` and then serializes it back to ZW text using `to_zw()`. This process normalizes indentation and spacing. If parsing fails, the original text is returned to prevent data loss.
    -   **Returns:** A prettified ZW text string, or the original string if parsing failed.

### Testing the Parser

A test script, `zw_mcp/test_zw_parser.py`, is provided to demonstrate and verify the functionality of the parser module. It can be run directly:

```bash
python3 zw_mcp/test_zw_parser.py
```
This script will output the results of parsing, prettifying, and reconstructing a sample ZW string, along with validation checks.

### Potential Uses:

-   **Validating Ollama Output:** Ensuring responses from Ollama adhere to expected ZW structures.
-   **Normalizing Memory Entries:** Cleaning up ZW text before storing it in memory logs or using it for future prompts.
-   **Data Transformation:** Converting ZW data to dictionaries for easier manipulation in Python or for export to other formats (like JSON, although `parse_zw` directly produces a Python dict which can then be easily serialized to JSON using Python's `json` library).
-   **Interfacing with External Tools:** Preparing ZW data for use in game engines (like Godot), creative tools (like Blender), or other CLI applications.

This parser is a key component for building more complex and reliable ZW-based applications. Future enhancements could include more detailed error reporting with line numbers, schema validation against predefined ZW structures, and more sophisticated list handling.
```
