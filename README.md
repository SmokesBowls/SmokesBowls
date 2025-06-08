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

---
## Phase 5: Multi-Agent Control Framework

This phase introduces a sophisticated multi-agent orchestration system, enabling multiple ZW-speaking agents, each with unique configurations, styles, and memory, to collaborate or hand off tasks in a sequential manner. All inter-agent communication is facilitated through the existing TCP daemon (`zw_mcp_daemon.py`).

### Core Components:

-   **`zw_mcp/zw_agent_hub.py` (Orchestrator):**
    -   The central script that manages the multi-agent sessions.
    -   Reads `zw_mcp/agent_profiles.json` to determine the sequence and configuration of agents to run.
    -   Initiates the process with a "master seed" prompt (`zw_mcp/prompts/master_seed.zw`).
    -   Runs each defined agent sequentially:
        -   The output from one agent becomes the initial input prompt for the next agent in the chain.
        -   Each agent session (which can include multiple internal rounds per agent) is managed by a reusable `run_single_agent_session` function within the hub. This function leverages the core logic from `ollama_agent.py` (e.g., for memory seeding, style application, internal looping, logging, and memory persistence for that specific agent).
    -   Prints status updates and the final output of the entire agent chain.

-   **`zw_mcp/agent_profiles.json` (Agent Definitions):**
    -   A JSON file that lists all available agents and points to their individual configuration files.
    -   **Example Structure:**
        ```json
        [
          {
            "name": "Narrator",
            "config": "zw_mcp/agents/narrator_config.json"
          },
          {
            "name": "Historian",
            "config": "zw_mcp/agents/historian_config.json"
          }
        ]
        ```

-   **`zw_mcp/agents/` (Directory for Individual Agent Configs):**
    -   This directory holds separate JSON configuration files for each agent (e.g., `narrator_config.json`, `historian_config.json`).
    -   Each configuration file follows the same format as the main `zw_mcp/agent_config.json` used by the standalone `ollama_agent.py`, allowing for unique settings per agent:
        -   `prompt_path`: Path to the agent's own initial seed prompt (used if not prepending or for its very first internal round if `prepend_previous_response` is false).
        -   `style`: Specific persona/role for this agent.
        -   `max_rounds`: How many internal loops this agent performs.
        -   `stop_keywords`: Words that will stop this agent's internal loop.
        -   `log_path`: Path to this agent's specific log file (e.g., in `zw_mcp/agent_runtime/`).
        -   `memory_enabled`, `memory_path`: Settings for this agent's specific memory.
        -   `use_memory_seed`, `memory_limit`: For this agent's initial prompt construction using its own memory.
        -   `prepend_previous_response`: Governs how this agent forms its own subsequent internal prompts.

-   **`zw_mcp/prompts/` (Directory for Seed Prompts):**
    -   Contains the initial seed prompts for each agent (e.g., `narrator_seed.zw`, `historian_seed.zw`) and the `master_seed.zw` for the hub.

-   **`zw_mcp/agent_runtime/` (Directory for Agent-Specific Outputs - Created Dynamically):**
    -   This directory is where individual agents will store their log files and memory files, as specified in their respective configuration files (e.g., `narrator.log`, `narrator_memory.json`).
    -   The directory and files are created when the agents run and logging/memory is enabled.

### How to Run the Multi-Agent Hub:

1.  **Ensure the ZW MCP Daemon is running:**
    The daemon acts as the communication layer for all agents.
    ```bash
    python3 zw_mcp/zw_mcp_daemon.py
    ```

2.  **Prepare Agent Configurations and Prompts:**
    -   Define your agents and their config paths in `zw_mcp/agent_profiles.json`.
    -   Create/edit the individual agent JSON config files in `zw_mcp/agents/`.
    -   Create/edit the corresponding seed prompt `.zw` files in `zw_mcp/prompts/`.
    -   Ensure the `master_seed.zw` in `zw_mcp/prompts/` contains the desired starting prompt for the entire chain.

3.  **Run the Agent Hub:**
    In a separate terminal (while the daemon is running):
    ```bash
    python3 zw_mcp/zw_agent_hub.py
    ```

4.  **Expected Behavior:**
    -   The hub will load `agent_profiles.json`.
    -   It will start with `master_seed.zw` as the input for the first agent.
    -   Each agent in the profile list will run sequentially.
        -   The console will show which agent is running and its interactions (prompts/responses for its internal rounds).
        -   Each agent will create/update its own log and memory files in `zw_mcp/agent_runtime/` as per its configuration.
    -   The final output from one agent is passed as the initial input prompt to the next agent.
    -   The hub will print the final output from the last agent in the chain upon completion.

### Updated Directory Structure (Illustrative for Phase 5):

```
zw_mcp/
├── agent_profiles.json       # NEW: Defines the sequence of agents
├── agents/                   # NEW: Directory for individual agent configs
│   ├── narrator_config.json
│   └── historian_config.json
├── agent_runtime/            # NEW (created dynamically): For per-agent logs & memory
│   ├── narrator.log
│   ├── narrator_memory.json
│   ├── historian.log
│   └── historian_memory.json
├── zw_agent_hub.py         # NEW: Orchestrator for multi-agent sessions
├── ollama_agent.py         # Core single-agent logic (used by the hub)
├── agent_config.json       # Default config for standalone ollama_agent.py
├── zw_mcp_daemon.py        # TCP Daemon server
├── client_example.py       # Example TCP client
├── zw_mcp_server.py        # Original CLI tool
├── ollama_handler.py       # Handles API requests to Ollama
├── zw_parser.py            # ZW parsing utilities
├── test_zw_parser.py       # Tests for zw_parser
├── prompts/
│   ├── example.zw
│   ├── master_seed.zw        # NEW: Initial prompt for the agent hub
│   ├── narrator_seed.zw    # NEW: Seed for Narrator agent
│   └── historian_seed.zw   # NEW: Seed for Historian agent
├── responses/
│   └──                     # Directory for saved CLI responses (zw_mcp_server.py)
└── logs/
    ├── agent.log           # Log for standalone ollama_agent.py
    ├── daemon.log          # Log for TCP daemon interactions
    ├── memory.json         # Memory for standalone ollama_agent.py
    └── session.log         # Log for CLI tool interactions (zw_mcp_server.py)
```

This multi-agent framework allows for the creation of complex, collaborative narrative simulations or problem-solving dialogues between different AI personas.
```

---
## Phase 6: Blender Adapter

This phase bridges the ZW protocol with 3D content creation by introducing an adapter script that runs within Blender. It allows ZW-formatted instructions to be translated into Blender Python (`bpy`) commands, effectively enabling ZW agents or scripts to "speak objects into existence."

### Core Component: `zw_mcp/blender_adapter.py`

-   **Purpose:** This Python script is designed to be executed by Blender's internal Python interpreter. It reads a specified ZW file, parses it using the existing `zw_mcp.zw_parser` module, and then processes the parsed structure to create 3D objects in the current Blender scene.
-   **Functionality:**
    -   **ZW Input:** Reads a designated `.zw` file (e.g., `zw_mcp/prompts/blender_scene.zw`) containing scene descriptions.
    -   **Parsing:** Utilizes `zw_parser.parse_zw()` to convert the ZW text into a Python dictionary.
    -   **ZW-to-bpy Mapping:** The `handle_zw_object_creation` function now processes a dictionary of attributes for each `ZW-OBJECT`. It extracts `TYPE`, `NAME`, `LOCATION`, and `SCALE`. `LOCATION` and `SCALE` string values (e.g., `"(1,2,3)"`) are parsed into tuples. These attributes are then used to create and configure Blender objects via `bpy.ops.mesh.primitive_..._add()` and by setting object properties.
    -   **Recursive Processing:** Traverses the parsed ZW dictionary, allowing for nested structures. It identifies ZW object definitions (both simple `ZW-OBJECT: <Type>` and more complex `ZW-OBJECT:\n  TYPE: <Type>\n  ...attributes`) and passes the necessary attribute dictionary to `handle_zw_object_creation`.
-   **Supported ZW Object Definition:**
    -   `ZW-OBJECT` can be defined simply (e.g., `ZW-OBJECT: Sphere`) or with attributes:
        ```zw
        ZW-OBJECT:
          TYPE: <TypeName>       // e.g., Cube, Sphere, Plane, Cone
          NAME: <ObjectNameString> // e.g., MyCube
          LOCATION: "(x, y, z)"  // e.g., "(1.0, -2.5, 0.0)"
          SCALE: "(sx, sy, sz)" // e.g., "(1, 1, 1)" or "2.0" (uniform)
        // Other attributes like MATERIAL might be present but not yet processed.
        ```
    -   **Core Supported Attributes:**
        -   `TYPE: <TypeName>` (e.g., Cube, Sphere, Plane, Cone)
        -   `NAME: <ObjectNameString>`
        -   `LOCATION: "(x, y, z)"` (string representation of a 3-tuple)
        -   `SCALE: "(sx, sy, sz)"` or `"s"` (string representation of a 3-tuple or a single float for uniform scaling)
    -   `LOCATION` is used at creation time. `NAME` and `SCALE` are applied to the newly created object.
    *(The adapter can be extended to support more object types, properties like rotation, materials, and more complex ZW command structures).*

### Phase 6.2: Object Parenting and Hierarchies with `CHILDREN`

To create structured scenes with parent-child relationships between objects, the ZW protocol now supports a `CHILDREN` key within a `ZW-OBJECT` definition. This allows for building complex hierarchies directly from ZW input.

#### ZW Syntax for Parenting:

The `CHILDREN` key expects a list of ZW-OBJECT definitions. Each object defined within this list will be parented to the `ZW-OBJECT` that contains the `CHILDREN` key.

**Example:**

```zw
ZW-OBJECT:
  TYPE: Cube
  NAME: ParentCube
  LOCATION: (0, 0, 1)
  SCALE: (2, 2, 0.5)
  CHILDREN: // List of child objects
    - ZW-OBJECT:
        TYPE: Sphere
        NAME: ChildSphere1
        LOCATION: (0, 0, 0.75) // Location is world, parenting preserves this
        SCALE: (0.4, 0.4, 0.4)
    - ZW-OBJECT:
        TYPE: Cone
        NAME: ChildCone1
        LOCATION: (0.8, 0, 0.5)
        SCALE: (0.1, 0.1, 0.8)
        CHILDREN: // Grandchildren are possible
          - ZW-OBJECT:
              TYPE: Sphere
              NAME: GrandChildSphere
              LOCATION: (0,0,0.4)
              SCALE: (0.05,0.05,0.05)
///

// Another top-level object (not part of the hierarchy above)
ZW-OBJECT:
  TYPE: Plane
  NAME: Ground
  SCALE: (10,10,1)
///
```

#### How it Works in `blender_adapter.py`:

-   When `process_zw_structure` encounters a `ZW-OBJECT`, it creates that object first.
-   If that ZW-OBJECT's definition includes a `CHILDREN` key (which must be a list):
    -   The adapter iterates through each item in the `CHILDREN` list. Each item is itself expected to be a `ZW-OBJECT` definition (i.e., a dictionary containing a `ZW-OBJECT` key whose value is the child's own attribute dictionary).
    -   For each child ZW-OBJECT definition, `process_zw_structure` is called recursively.
    -   Crucially, the newly created parent Blender object is passed as the `parent_bpy_obj` argument to these recursive calls.
-   The `handle_zw_object_creation` function, when it receives a `parent_bpy_obj`, sets the newly created Blender object's parent to `parent_bpy_obj` using `bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)`. This ensures the child object maintains its specified world location, rotation, and scale at the moment of parenting.

#### Result in Blender:

-   Objects defined under a `CHILDREN` key will appear nested under their parent object in Blender's Outliner.
-   Transforming the parent object (moving, rotating, scaling) will correspondingly affect all its child objects.

This feature is essential for creating complex, articulated models, organizing scenes logically, and enabling more sophisticated procedural generation directly from ZW descriptions.

### Phase 6.3: Materials and Appearance

This enhancement allows ZW definitions to specify visual properties for objects, including material names, colors, shading types, and detailed shader parameters using Blender's Principled BSDF shader.

#### ZW Syntax for Materials and Appearance:

These attributes are added within a `ZW-OBJECT` definition:

```zw
ZW-OBJECT:
  TYPE: Cube
  NAME: SampleMaterialBox
  LOCATION: (0, 0, 1)
  // ... other attributes like SCALE, CHILDREN ...
  MATERIAL: MyCustomMaterial  // A name for the material
  COLOR: "#FF6347"           // Tomato color (hex)
  SHADING: Smooth             // "Smooth" or "Flat"
  BSDF:                     // Detailed Principled BSDF parameters
    METALLIC: 0.8
    ROUGHNESS: 0.25
    SPECULAR: 0.6
    ALPHA: 0.9             // For transparency
    // Add other Principled BSDF inputs here, e.g., Base_Color, Emission_Color, etc.
///
```

#### Attribute Breakdown:

-   **`MATERIAL: <String>`**
    -   Provides a name for the Blender material (e.g., "ShinyMetal", "CharacterSkin").
    -   If a material with this name exists, the adapter may try to use/update it (current behavior is to create if not exact name match, or use if exact match). If not specified, a name is generated (e.g., `ObjectName_Mat`).

-   **`COLOR: "<#RRGGBB>" | "(R,G,B)" | "(R,G,B,A)"`**
    -   Sets the base color of the object's material.
    -   Accepts a hex string (e.g., `"#FF4500"`) or a string representation of an RGB or RGBA tuple (e.g., `"(0.8, 0.2, 0.1)"` or `"(0.8, 0.2, 0.1, 1.0)"`). Values should be 0-1 for tuples.
    -   The adapter includes a `parse_color()` function to handle these formats.

-   **`SHADING: Smooth | Flat`**
    -   Determines the object's mesh shading.
    -   `"Smooth"` results in `bpy.ops.object.shade_smooth()`.
    -   `"Flat"` results in `bpy.ops.object.shade_flat()`. Defaults to "Smooth" if not specified.

-   **`BSDF: { <PropertyName>: <Value>, ... }`**
    -   A dictionary block allowing direct control over Blender's Principled BSDF shader inputs.
    -   `<PropertyName>` should correspond to valid input names on the Principled BSDF node (e.g., `METALLIC`, `ROUGHNESS`, `SPECULAR`, `ALPHA`, `Base_Color` - note space for "Base Color"). ZW keys are typically converted (e.g., `BASE_COLOR` to "Base Color").
    -   `<Value>` is usually a float, but colors can also be set here (e.g., `Base_Color: "(1,0,0,1)"`).

#### Attribute Precedence for Material Application:

The `blender_adapter.py` applies these attributes with the following precedence to define the material:
1.  **`BSDF` properties**: If a `BSDF` block is provided, its settings (including any "Base Color" set within it) take highest precedence for controlling the Principled BSDF shader.
2.  **`COLOR` attribute**: If a `COLOR` attribute is specified outside the `BSDF` block, it will set the "Base Color" of the Principled BSDF, *unless* the "Base Color" was already set by a `Base_Color` key within the `BSDF` block.
3.  **`MATERIAL` name**: This is used to name the material in Blender. If neither `BSDF` nor `COLOR` provides color information, a default material with this name is created.

#### How it Works in `blender_adapter.py`:

-   The `handle_zw_object_creation` function in `blender_adapter.py` is responsible for processing these attributes.
-   It retrieves or creates a Blender material.
-   It ensures the material uses nodes and accesses the Principled BSDF shader node.
-   It then applies the `BSDF` dictionary values directly to the shader inputs.
-   If applicable, it sets the "Base Color" from the `COLOR` attribute.
-   Finally, it assigns the configured material to the object and applies the specified `SHADING`.

This system allows for a flexible range of visual definitions, from simple named materials or colored objects to finely tuned PBR (Physically Based Rendering) appearances via the BSDF properties.

### Phase 6.4: Collections and Grouping

To improve scene organization and management within Blender, the ZW protocol now supports assigning objects to specific **Collections** and defining named collection groups.

#### ZW Syntax for Collections:

Two primary methods are available for organizing objects into Blender Collections:

1.  **Explicit `COLLECTION` Attribute on `ZW-OBJECT`**:
    Assigns an individual object directly to a named Blender Collection. If the collection doesn't exist at the top level of the scene, it will be created.

    ```zw
    ZW-OBJECT:
      TYPE: Sphere
      NAME: My孤立Sphere // "MyIsolatedSphere"
      LOCATION: (5, 5, 5)
      COLLECTION: SpecialEffects // This sphere will be in "SpecialEffects" collection
    ///
    ```

2.  **`ZW-COLLECTION` Block for Scoped Grouping**:
    Defines a named Blender Collection and places all `ZW-OBJECT`s (and nested `ZW-COLLECTION`s) defined within its `CHILDREN` list into this collection.
    The ZW parser is expected to handle `ZW-COLLECTION: <CollectionName>` as the key, where `<CollectionName>` is the desired name for the collection in Blender. The value associated with this key should be a dictionary, typically containing a `CHILDREN` list.
    Alternatively, if the ZW is structured as `ZW-COLLECTION:
  NAME: <CollectionName>
  CHILDREN: ...`, the adapter will use the `NAME` attribute for the collection. (The current adapter implementation primarily expects the collection name as part of the key like `ZW-COLLECTION: MyGroup`).

    **Example:**
    ```zw
    ZW-COLLECTION: EnvironmentProps // Creates/uses "EnvironmentProps" collection
      CHILDREN:
        - ZW-OBJECT:
            TYPE: Cube
            NAME: Rock01
            LOCATION: (10, 0, 0.5)
        - ZW-OBJECT:
            TYPE: Cube
            NAME: Rock02
            LOCATION: (10.5, 0.2, 0.5)
        - ZW-COLLECTION: Foliage // Nested collection "Foliage" within "EnvironmentProps"
            CHILDREN:
              - ZW-OBJECT:
                  TYPE: Cone
                  NAME: Tree01
                  LOCATION: (12, 0, 1.5)
                  COLLECTION: ForestAssets // This object goes into "ForestAssets", not "Foliage" or "EnvironmentProps"
                                          // due to explicit assignment taking precedence for the object itself.
              - ZW-OBJECT:
                  TYPE: Sphere
                  NAME: Bush01
                  LOCATION: (12.5,0.5,0.25)
                  // This object will be in the "Foliage" collection.
    ///
    ```

#### How it Works in `blender_adapter.py`:

-   **`get_or_create_collection(name, parent_collection=None)`**: A helper function is used to retrieve an existing Blender Collection by name or create a new one. If `parent_collection` is provided, the new collection is created as its child, allowing for nested collection structures.
-   **`process_zw_structure(data_dict, parent_bpy_obj=None, current_bpy_collection=None)`**:
    -   This function now manages a `current_bpy_collection` context (defaulting to the scene's master collection).
    -   **Handling `ZW-COLLECTION: <Name>` keys**: When such a key is encountered, the adapter calls `get_or_create_collection` for `<Name>`, using the `current_bpy_collection` as its parent. All ZW definitions within this block's `CHILDREN` list are then processed with this new collection as their `current_bpy_collection`.
    -   **Handling `ZW-OBJECT`**:
        -   After a Blender object is created, the adapter determines its final collection.
        -   If the ZW-OBJECT has an explicit `COLLECTION: <SpecificName>` attribute, that object is linked to the `<SpecificName>` collection (which is created at the scene's top level if it doesn't exist). This overrides any inherited collection context for that specific object.
        -   Otherwise, the object is linked to the `current_bpy_collection` passed down by its parent ZW structure (either a `ZW-COLLECTION` block or the scene's default collection).
        -   The object is unlinked from any other collections (like the default scene collection if it was placed there temporarily) to ensure it resides only in its intended target collection.
    -   Children of a `ZW-OBJECT` (defined under its `CHILDREN` key for parenting) will inherit the collection of their parent `ZW-OBJECT` as their `current_bpy_collection` context, unless they themselves have an explicit `COLLECTION` attribute or are within a nested `ZW-COLLECTION` block.

#### Result in Blender:

-   Objects will be organized into the specified collections in Blender's Outliner.
-   `ZW-COLLECTION` blocks allow for creating hierarchical collection structures.
-   This enables easier management, visibility toggling, and selection of object groups within complex scenes.

This collection system provides a powerful way to structure and manage ZW-generated scenes, mirroring common practices in 3D production workflows.

### Phase 6.6: Procedural Logic Nodes with `ZW-FUNCTION`

This phase introduces the `ZW-FUNCTION` block, allowing ZW definitions to drive procedural modeling operations within Blender using its powerful Geometry Nodes system. This enables the creation of parametric and generative content directly from ZW commands.

#### ZW Syntax for Functions:

A `ZW-FUNCTION` is defined as a block with the following structure:

```zw
ZW-FUNCTION:
  NAME: <OptionalDescriptiveName> // For logging or debugging
  TARGET: <TargetObjectName>     // Name of an existing ZW-OBJECT to modify or use as source
  OPERATION: <OperationType>     // E.g., ARRAY, DISPLACE_NOISE
  PARAMS:                       // Dictionary of parameters specific to the OPERATION
    <ParamName1>: <Value1>
    <ParamName2>: <Value2>
    // ...
///
```

-   **`NAME`**: An optional name for this function call, useful for identification.
-   **`TARGET`**: The `NAME` of a previously defined `ZW-OBJECT` that this function will operate on (either by modifying it or using it as a source).
-   **`OPERATION`**: A string identifying the type of procedural operation to perform.
-   **`PARAMS`**: A nested dictionary of parameters that control the specified `OPERATION`.

#### Initially Supported Operations:

The `blender_adapter.py` processes these `ZW-FUNCTION` blocks by adding and configuring Geometry Node modifiers on the target objects (or on new host objects for generative operations like ARRAY).

1.  **`OPERATION: ARRAY`**
    -   **Purpose:** Creates a linear array of instances of the `TARGET` object.
    -   **Behavior:** A new empty host object is created in Blender. A Geometry Nodes modifier is added to this host, which instances the original `TARGET` object.
    -   **Key `PARAMS`:**
        -   `COUNT: <Integer>`: The number of instances to create in the array (e.g., `5`).
        -   `OFFSET: "(x, y, z)"`: A string tuple defining the offset vector between each instance (e.g., `"(2.0, 0, 0)"`).
        -   `MODE: INSTANCE | REALIZE` (Optional): Defaults to `INSTANCE`. If `REALIZE`, the instances are converted to real geometry.
    -   **Example:**
        ```zw
        ZW-OBJECT:
          TYPE: Cylinder
          NAME: PillarUnit
          SCALE: (0.2, 0.2, 1.5)
        ///

        ZW-FUNCTION:
          NAME: CreatePillarRow
          TARGET: PillarUnit
          OPERATION: ARRAY
          PARAMS:
            COUNT: 6
            OFFSET: "(0, 2.0, 0)" // Array along Y-axis
        ///
        ```

2.  **`OPERATION: DISPLACE_NOISE`**
    -   **Purpose:** Modifies the geometry of the `TARGET` object by displacing its vertices using a procedural noise texture.
    -   **Behavior:** Adds and configures a Geometry Nodes modifier directly on the `TARGET` object. For best results, the target object should have sufficient geometry (subdivisions).
    -   **Key `PARAMS`:**
        -   `SCALE: <Float>`: The scale of the noise texture (controls frequency, e.g., `3.0`).
        -   `STRENGTH: <Float>`: The magnitude of the displacement (e.g., `0.5`).
        -   `AXIS: X | Y | Z | NORMAL` (Optional): The axis or direction of displacement. Defaults to `Z` or `NORMAL` depending on implementation. (Current implementation primarily supports X, Y, or Z via `Combine XYZ` node).
        -   `SEED: <Integer>` (Optional): A seed value for the noise texture to vary the pattern (passed to W-input of Noise Texture node).
    -   **Example:**
        ```zw
        ZW-OBJECT:
          TYPE: Plane
          NAME: GroundPlane
          SCALE: (20, 20, 1)
          // Consider adding subdivisions via another function or manually for good displacement
        ///

        ZW-FUNCTION:
          NAME: SculptTerrainSurface
          TARGET: GroundPlane
          OPERATION: DISPLACE_NOISE
          PARAMS:
            SCALE: 5.0
            STRENGTH: 0.75
            AXIS: Z
        ///
        ```

#### How it Works in `blender_adapter.py`:

-   The `process_zw_structure` function now recognizes `ZW-FUNCTION` keys.
-   It calls `handle_zw_function_block`, which acts as a dispatcher based on the `OPERATION` string.
-   Specific functions like `apply_array_gn` and `apply_displace_noise_gn` are responsible for:
    -   Finding the target Blender object(s).
    -   Creating a new host object if the operation is generative (like `ARRAY`).
    -   Adding a Geometry Nodes modifier to the appropriate object.
    -   Programmatically constructing a node tree within the modifier's node group. This involves creating nodes (e.g., Object Info, Mesh Line, Instance on Points, Set Position, Noise Texture, Combine XYZ, Vector Math, Group Input, Group Output) and linking their sockets.
    -   Setting the input values of these nodes based on the `PARAMS` from the ZW definition.

This initial implementation of `ZW-FUNCTION` provides a powerful pathway to defining procedural geometry directly within the ZW protocol, enabling more dynamic and complex scene generation in Blender. Future extensions can add more operations, more sophisticated parameter handling, and exposure of Geometry Node Group inputs directly.

### Phase 6.7: Interactive Drivers with `ZW-DRIVER`

This phase introduces the `ZW-DRIVER` block, enabling the creation of dynamic relationships between object properties within Blender. This allows one property to control another, potentially through a scripted expression, bringing more interactivity and procedural linkage to ZW-defined scenes.

#### ZW Syntax for Drivers:

A `ZW-DRIVER` block defines a single driver relationship:

```zw
ZW-DRIVER:
  NAME: <OptionalDriverName>          // An optional name for the driver itself (for debugging/identification)
  SOURCE_OBJECT: <SourceObjectName>   // The NAME of the Blender object whose property will drive the target
  SOURCE_PROPERTY: "<RNA_DataPath>"   // The RNA data path to the source property (e.g., "location.x", "scale[2]", "modifiers['MyModifierName'].some_value")
  TARGET_OBJECT: <TargetObjectName>   // The NAME of the Blender object whose property will be driven
  TARGET_PROPERTY: "<RNA_DataPath>"   // The RNA data path to the target property (e.g., "rotation_euler[0]", "material_slots[0]...")
  EXPRESSION: "<PythonExpression>"   // A Python expression. The source property's value is available as 'var'. E.g., "var * 2.0 + 0.5"
///
```

-   **`NAME`** (Optional): A descriptive name for this driver setup.
-   **`SOURCE_OBJECT`**: The name of the Blender object that provides the input value for the driver.
-   **`SOURCE_PROPERTY`**: The specific property (RNA data path) on the `SOURCE_OBJECT` to use as input. Examples: `"location.x"`, `"scale[2]"`, `"rotation_euler[0]"`.
-   **`TARGET_OBJECT`**: The name of the Blender object whose property will be controlled by this driver.
-   **`TARGET_PROPERTY`**: The specific property (RNA data path) on the `TARGET_OBJECT` to be driven. This property will have a driver added to it. The path can include array indices like `location[0]` or be a direct property like `rotation_euler.x` (though the adapter uses `driver_add('rotation_euler', 0)` for the latter).
-   **`EXPRESSION`**: A Python expression string that defines how the source property's value (available as the variable `var` in the expression) is transformed to set the target property. If omitted, it defaults to `"var"` for a direct copy.

#### How it Works in `blender_adapter.py`:

-   The `process_zw_structure` function now recognizes `ZW-DRIVER` keys.
-   It calls `handle_zw_driver_block` with the associated dictionary of driver parameters.
-   `handle_zw_driver_block`:
    1.  Retrieves the source and target Blender objects by their names.
    2.  Uses `target_obj.driver_add(rna_path_to_target_prop, index_if_any)` to add a driver to the specified target property.
    3.  Configures the driver:
        -   Sets its `type` to `'SCRIPTED'`.
        -   Sets its `expression` to the provided ZW `EXPRESSION`.
    4.  Adds a driver variable (typically named `var`):
        -   Sets its `type` to `'SINGLE_PROP'`.
        -   Links its target to the `SOURCE_OBJECT` (`id_type = 'OBJECT'`, `id = source_obj`).
        -   Sets its `data_path` to the `SOURCE_PROPERTY` from the ZW definition.
-   This creates a live link where changes to the source property dynamically update the target property according to the expression.

#### Example:

```zw
ZW-OBJECT:
  TYPE: Cube
  NAME: ControlCube
  LOCATION: (0,0,1)
///

ZW-OBJECT:
  TYPE: Sphere
  NAME: DrivenSphere
  LOCATION: (0,2,1)
  SCALE: (0.5,0.5,0.5)
///

ZW-DRIVER:
  NAME: CubeX_Drives_SphereZScale
  SOURCE_OBJECT: ControlCube
  SOURCE_PROPERTY: "location.x"
  TARGET_OBJECT: DrivenSphere
  TARGET_PROPERTY: "scale[2]" // Drives the Z-scale (index 2 for Z)
  EXPRESSION: "var * 0.3 + 0.1" // Sphere's Z-scale = ControlCube.location.x * 0.3 + 0.1
///
```
In this example, moving the `ControlCube` along its X-axis will dynamically change the Z-scale of the `DrivenSphere`.

This `ZW-DRIVER` functionality opens up possibilities for creating more dynamic and interconnected scenes directly from ZW, forming a bridge towards more complex animation and rigging setups.

### Phase 6.8: Keyframe Animations with `ZW-ANIMATION`

This phase empowers the ZW protocol to define explicit keyframed animations for object properties in Blender, allowing for direct control over how objects change over time.

#### ZW Syntax for Animations:

The `ZW-ANIMATION` block is used to define a set of keyframes for one or more related animation channels (F-Curves) on a target object.

```zw
ZW-ANIMATION:
  NAME: <OptionalAnimationName>      // Optional descriptive name for this animation block
  TARGET_OBJECT: <TargetObjectName>  // The NAME of the ZW-OBJECT to animate
  PROPERTY_PATH: "<RNA_Property>"    // The base RNA property path (e.g., "location", "rotation_euler", "scale")
                                     // Can also be a path to a custom property or material node input.
  INDEX: <OptionalInteger>          // Specify for single component of a vector (e.g., 0 for X, 1 for Y, 2 for Z).
                                     // If omitted and VALUE is a tuple, all components are animated.
  UNIT: degrees                     // Optional. Use "degrees" for rotation properties if KEYFRAME VALUEs are in degrees.
                                     // Adapter converts to radians for Blender. Defaults to Blender's native units (radians for rotation).
  INTERPOLATION: <BEZIER|LINEAR|CONSTANT> // Optional. Sets interpolation for all keyframes in this block. Defaults to "BEZIER".
  KEYFRAMES:                         // List of keyframe definitions
    - FRAME: <FrameNumber>
      VALUE: <ScalarOrTupleString>   // e.g., 90, "0.5", "(1.0, 2.0, 3.0)"
    - FRAME: <FrameNumber>
      VALUE: <ScalarOrTupleString>
    // ... more keyframes
///
```

-   **`NAME`** (Optional): A name for this animation sequence, mainly for clarity or debugging.
-   **`TARGET_OBJECT`**: The `NAME` of the ZW-OBJECT in Blender that will be animated.
-   **`PROPERTY_PATH`**: The Blender RNA data path to the property to be animated (e.g., `"location"`, `"rotation_euler"`, `"scale"`). For more advanced uses, this could target material properties like `"material_slots['MatName'].material.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value"`.
-   **`INDEX`** (Optional): If `PROPERTY_PATH` refers to a multi-component property (like `location` which is a vector of X,Y,Z), `INDEX` specifies which component to animate (0 for X, 1 for Y, 2 for Z). If `INDEX` is omitted, and `VALUE` in `KEYFRAMES` is a tuple string, the adapter will attempt to animate all components of the property.
-   **`UNIT`** (Optional): If set to `"degrees"` and `PROPERTY_PATH` is a rotational property (e.g., `"rotation_euler"`), the `VALUE`s in `KEYFRAMES` are assumed to be in degrees and will be converted to radians by the adapter. Otherwise, values are used as-is (Blender's default for rotation is radians).
-   **`INTERPOLATION`** (Optional): Specifies the interpolation type for the keyframes created by this block. Supported values: `"BEZIER"` (default), `"LINEAR"`, `"CONSTANT"`. This is applied to each created keyframe point.
-   **`KEYFRAMES`**: A list of dictionaries, where each dictionary defines a single keyframe with:
    -   `FRAME: <Integer>`: The frame number for this keyframe.
    -   `VALUE: <ScalarOrTupleString>`: The value of the property at this frame.
        -   If `INDEX` is specified, `VALUE` should be a single number (or a string parsable to one).
        -   If `INDEX` is *not* specified and `PROPERTY_PATH` is a vector type (e.g., `"location"`), `VALUE` should be a string representing a tuple (e.g., `"(1.0, 2.0, 3.0)"`). The adapter will parse this and create keyframes for each component (X, Y, Z).

#### How it Works in `blender_adapter.py`:

-   The `process_zw_structure` function detects `ZW-ANIMATION` keys and passes the definition to `handle_zw_animation_block`.
-   `handle_zw_animation_block`:
    1.  Retrieves the target Blender object.
    2.  Ensures the object has `animation_data` and an `action` (creating them if necessary). An action name can be derived from the `TARGET_OBJECT` and `PROPERTY_PATH` or the optional `NAME` field of the `ZW-ANIMATION` block.
    3.  For each entry in the `KEYFRAMES` list:
        -   It parses the `FRAME` number and `VALUE`.
        -   If animating a vector property (like "location") without a specific `INDEX`, it parses the tuple string `VALUE` and creates/updates F-Curves for each component (X, Y, Z).
        -   If an `INDEX` is provided (or for a scalar property), it creates/updates the F-Curve for that specific component/property.
        -   It converts `VALUE` to radians if `UNIT: degrees` is specified for rotational properties.
        -   It uses `fcurve.keyframe_points.insert(frame, value)` to add the keyframe.
        -   It sets the `keyframe_point.interpolation` based on the `INTERPOLATION` type specified in the ZW block.
    -   Helper functions like `ensure_fcurve` and `set_keyframe_interpolation` assist in this process.

#### Examples:

**1. Single-axis rotation (Z-axis) with LINEAR interpolation:**
```zw
ZW-OBJECT:
  TYPE: Cube
  NAME: MyRotatingCube
///
ZW-ANIMATION:
  TARGET_OBJECT: MyRotatingCube
  PROPERTY_PATH: "rotation_euler"
  INDEX: 2 // Z-axis
  UNIT: degrees
  INTERPOLATION: LINEAR
  KEYFRAMES:
    - FRAME: 1
      VALUE: 0
    - FRAME: 60
      VALUE: 360
///
```

**2. Multi-axis location animation (X,Y,Z) with BEZIER interpolation (default):**
```zw
ZW-OBJECT:
  TYPE: Sphere
  NAME: BouncingBall
///
ZW-ANIMATION:
  TARGET_OBJECT: BouncingBall
  PROPERTY_PATH: "location" // Animates X, Y, Z location
  // UNIT defaults to Blender units
  // INTERPOLATION defaults to BEZIER
  KEYFRAMES:
    - FRAME: 1
      VALUE: "(0,0,5)"  // Start high
    - FRAME: 15
      VALUE: "(0,0,1)"  // Hit ground
    - FRAME: 30
      VALUE: "(0,0,3)"  // Bounce up
    - FRAME: 45
      VALUE: "(0,0,1)"  // Hit ground again
///
```

This `ZW-ANIMATION` system provides a robust way to define complex movements and changes over time directly within the ZW protocol, further enhancing its capability as a scene description and control language.

---
## Phase 6.5: ZW Roundtrip (Blender to ZW Export)

This phase introduces the capability to export Blender scene data back into the ZW format, enabling a "roundtrip" workflow where scenes can be defined in ZW, modified or created in Blender, and then re-serialized as ZW. This is crucial for hybrid human-AI design processes and for capturing Blender scene states in the ZW protocol.

### Core Component: `zw_mcp/blender_exporter.py`

-   **Purpose:** This Python script is designed to be executed by Blender's internal Python interpreter. It inspects the Blender scene (either selected objects or all mesh objects) and converts their properties back into a ZW-formatted text string, which is then saved to a file.
-   **Functionality:**
    -   **Scope of Export:**
        -   Can export either only currently selected mesh objects or all mesh objects in the active scene. This is controlled by a command-line argument (`--all`).
    -   **Attribute Export:** For each exported mesh object, the script attempts to extract and format the following properties:
        -   `TYPE`: Determined by checking a custom property `obj.get("ZW_TYPE")` first. If not found, it uses heuristics based on `obj.data.name` (e.g., "Cube", "Sphere"). Defaults to "Mesh" if undetermined.
        -   `NAME`: The object's name in Blender (`obj.name`).
        -   `LOCATION`: The object's location (`obj.location`) formatted as `"(x, y, z)"`.
        -   `SCALE`: The object's scale (`obj.scale`) formatted as `"(sx, sy, sz)"`.
        -   `ROTATION`: The object's Euler rotation (`obj.rotation_euler`) formatted as `"(rx, ry, rz)"` (in radians).
        -   `MATERIAL`: If the object has materials, the name of the first material (`obj.data.materials[0].name`).
        -   `COLOR`: If a material is present, attempts to get the "Base Color" from its Principled BSDF node and formats it as `"#RRGGBB"`.
        -   `PARENT`: If the object is parented, the name of its parent object (`obj.parent.name`).
        -   `COLLECTION`: The name of the first collection the object belongs to (from `obj.users_collection[0].name`, if available).
    -   **ZW Output Structure (First Pass - Flat List):**
        -   The exporter generates a flat list of `ZW-OBJECT:` blocks. Each block represents one exported Blender object and its attributes.
        -   Hierarchical relationships (parenting, collections) are represented as attributes (`PARENT: <ParentName>`, `COLLECTION: <CollectionName>`) within each object's block, rather than through nested ZW structures like `CHILDREN:` or `ZW-COLLECTION:` blocks in this initial version.
        -   The existing `zw_parser.to_zw()` function is used to format the dictionary of each object's attributes into a valid ZW string block.
    -   **Output File:** The generated ZW text is saved to a user-specified output file path.

### Helper Functions in `blender_exporter.py`:

-   `format_vector_to_zw(vector, precision=3)`: Converts Blender `Vector` objects to ZW tuple strings.
-   `format_color_to_zw_hex(rgba_color)`: Converts Blender RGBA colors to ZW hex color strings.
-   `get_object_zw_type(blender_obj)`: Implements the logic for determining the ZW `TYPE` string.

### How to Use the ZW Exporter:

The `blender_exporter.py` script is primarily intended to be run from the command line using Blender in background mode, but can also be run from Blender's scripting tab if arguments are hardcoded or handled differently.

1.  **Prerequisites:**
    -   Blender installed.
    -   The ZW MCP project files structured as per the repository (especially `zw_parser.py` accessible to Blender).

2.  **Prepare Your Blender Scene:**
    -   Open or create a scene in Blender.
    -   If you want to export only specific objects, select them in Blender.
    -   If you want to ensure ZW `TYPE` is accurately exported for objects previously imported from ZW, make sure they have the `ZW_TYPE` custom property (the importer, `blender_adapter.py`, would need to be updated to set this if not already doing so).

3.  **Run from Command Line:**
    Open your terminal or command prompt, navigate to the root directory of the ZW MCP project, and execute:
    ```bash
    blender --background --python zw_mcp/blender_exporter.py -- --output path/to/your/exported_scene.zw
    ```
    -   `--background`: Runs Blender without the UI.
    -   `--python zw_mcp/blender_exporter.py`: Specifies the script to run.
    -   `--`: This special separator indicates that subsequent arguments are for the Python script, not for Blender itself.
    -   `--output <filepath>`: **(Required)** Specifies the path (including filename, e.g., `my_export.zw`) where the generated ZW text will be saved.
    -   `--all`: **(Optional)** If this flag is included, all mesh objects in the current scene will be exported. If omitted, only currently selected mesh objects will be exported.

    **Example exporting all mesh objects:**
    ```bash
    blender --background --python zw_mcp/blender_exporter.py -- --output exports/scene_dump.zw --all
    ```

4.  **Output:**
    -   A `.zw` file will be created at the specified output path, containing the ZW representation of the exported Blender objects.
    -   The console output from Blender (visible if not fully backgrounded or if logged) will show progress and any error messages from the script.

### Example of Exported ZW (Flat Structure):

```zw
# Exported from Blender by ZW Exporter v0.1
# --- Object Start ---
ZW-OBJECT:
  TYPE: Cube
  NAME: MyCube
  LOCATION: (1.0, 2.0, 3.0)
  SCALE: (1.0, 1.0, 1.0)
  ROTATION: (0.0, 0.0, 0.785) // Radians
  MATERIAL: RedMaterial
  COLOR: "#FF0000"
  COLLECTION: MainProps
///
# --- Object Start ---
ZW-OBJECT:
  TYPE: Sphere
  NAME: MySphere
  LOCATION: (-2.0, 0.5, 1.0)
  SCALE: (0.5, 0.5, 0.5)
  ROTATION: (0.0, 0.0, 0.0)
  PARENT: MyCube
  MATERIAL: BlueMaterial
  COLOR: "#0000FF"
  COLLECTION: MainProps
///
// ... more objects ...
```
*(Note: The exact separator between objects might vary slightly based on `to_zw` and how blocks are joined, but it will be a sequence of ZW-OBJECT definitions).*

This initial version of the ZW exporter provides a vital link for bringing Blender scene information back into the ZW ecosystem, paving the way for more advanced features like scene comparison, delta generation, or AI-assisted refinement of human-made Blender scenes via ZW.

### How to Use the Blender Adapter:

1.  **Prerequisites:**
    -   Blender installed.
    -   The ZW MCP project files structured as per the repository.

2.  **Prepare ZW Input:**
    -   Create or edit a `.zw` file with scene instructions. An example is provided at `zw_mcp/prompts/blender_scene.zw`.
        ```zw
        // Example ZW for blender_adapter.py
        ZW-OBJECT:
          TYPE: Cube
          NAME: ControlCube
          LOCATION: (1, 2, 3)
          SCALE: (1.0, 2.0, 0.5)
        ///
        ZW-OBJECT:
          TYPE: Sphere
          NAME: Orbiter
          LOCATION: (-2, 0, 5)
        ///
        ```

3.  **Run from Command Line (Headless/Background):**
    Open your terminal or command prompt, navigate to the root directory of the ZW MCP project, and execute:
    ```bash
    blender --background --python zw_mcp/blender_adapter.py
    ```
    -   `--background`: Runs Blender without opening the UI (headless).
    -   `--python <script_path>`: Tells Blender to execute the specified Python script.
    -   Objects defined in your `blender_scene.zw` will be created in a new Blender scene. To save the result, you would typically add `bpy.ops.wm.save_as_mainfile(filepath="path/to/your_scene.blend")` to the end of `blender_adapter.py`.

4.  **Run from Blender's Scripting Tab (Interactive):**
    -   Open Blender.
    -   Go to the "Scripting" tab.
    -   Click "Open" and navigate to `zw_mcp/blender_adapter.py` to load it into the text editor.
    -   Click the "Run Script" button (looks like a play icon).
    -   Objects will be created in your currently open Blender scene. This is useful for development and debugging.

### Important Notes for `blender_adapter.py`:

-   **Python Environment:** The script runs within Blender's own Python environment, which includes the `bpy` module.
-   **Importing `zw_parser`:** The `blender_adapter.py` includes logic to help Blender's Python interpreter find the `zw_parser.py` module located within the `zw_mcp` directory. This usually works best if Blender is launched from the root of the project directory.
-   **Error Handling & Logging:** The adapter includes print statements for progress and basic error handling. When run in background mode, Blender's console output will show these messages.

### Updated Directory Structure (Illustrative for Phase 6):

The `blender_adapter.py` is added to the `zw_mcp` directory, and a specific prompt file for it is in `prompts`.

```
zw_mcp/
├── blender_adapter.py      # NEW: Script to run within Blender
├── agent_profiles.json
├── agents/
│   ├── narrator_config.json
│   └── historian_config.json
├── agent_runtime/
│   # ... (per-agent logs/memory)
├── zw_agent_hub.py
├── ollama_agent.py
├── agent_config.json
├── zw_mcp_daemon.py
├── client_example.py
├── zw_mcp_server.py
├── ollama_handler.py
├── zw_parser.py
├── test_zw_parser.py
├── prompts/
│   ├── blender_scene.zw    # NEW: Example ZW input for Blender
│   ├── example.zw
│   ├── master_seed.zw
│   ├── narrator_seed.zw
│   └── historian_seed.zw
# ... (other directories like responses/, logs/)
```

This adapter represents a significant step towards using ZW as a descriptive language for generating and manipulating 3D content, opening possibilities for agent-driven world-building or procedural asset creation.
```
