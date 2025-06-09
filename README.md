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

4.  **Expected Output & Behavior:**
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

4.  **`TYPE: PROPERTY_ANIM`**
    -   **Purpose:** Provides a generic way to animate almost any animatable property of an object or its data over time using keyframes. This is similar to `ZW-ANIMATION` but within the `ZW-STAGE` context.
    -   **Specific Parameters:**
        -   `TARGET: <TargetObjectNameString>`: The name of the ZW-OBJECT to animate.
        -   `PROPERTY_PATH: "<RNA_Property>"`: The Blender RNA data path to the property (e.g., "location", "scale[0]", "modifiers['MyBevel'].width", "material_slots[0].material.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value").
        -   `INDEX: <OptionalInteger>`: Specify for a single component of a vector/array property if `VALUE` is scalar.
        -   `UNIT: degrees` (Optional): If `PROPERTY_PATH` is rotational and `VALUE`s are in degrees.
        -   `INTERPOLATION: <BEZIER|LINEAR|CONSTANT>` (Optional): Default is "BEZIER".
        -   `KEYFRAMES: [{FRAME: <F>, VALUE: <V>}, ...]` : List of keyframe definitions. `VALUE` can be scalar or tuple string.
    -   **Behavior:** Creates F-Curves and keyframes for the specified property, similar to `ZW-ANIMATION` processing.
    -   **Example:**
        ```zw
        ZW-STAGE:
          TRACKS:
            - TYPE: PROPERTY_ANIM
              TARGET: "StageFXLight"       // A ZW-LIGHT or ZW-OBJECT
              PROPERTY_PATH: "data.energy" // Animating light energy
              INTERPOLATION: BEZIER
              KEYFRAMES:
                - FRAME: 100
                  VALUE: 0.0
                - FRAME: 120
                  VALUE: 800.0
                - FRAME: 140
                  VALUE: 0.0
        ///
        ```

5.  **`TYPE: MATERIAL_OVERRIDE`**
    -   **Purpose:** Temporarily changes the material assigned to an object's material slot for a specified duration.
    -   **Specific Parameters:**
        -   `TARGET: <TargetObjectNameString>`: The ZW-OBJECT whose material will be changed.
        -   `MATERIAL_NAME: <MaterialToAssignString>`: The name of the Blender material to assign. The adapter will use an existing material or create a new one with this name (and default node setup if new).
        -   `START_FRAME: <Integer>`: Frame at which the new material is applied.
        -   `END_FRAME: <OptionalInteger>`: Frame at which to restore the original material.
        -   `RESTORE_ON_END: "true" | "false"` (Optional): Boolean (as string). If "true" and `END_FRAME` is specified, the object's material at `START_FRAME - 1` is restored at `END_FRAME`. Defaults to "false" or no restoration if `END_FRAME` is missing.
        -   `SLOT_INDEX: <OptionalInteger>`: The material slot index to target. Defaults to 0.
    -   **Behavior:** Keyframes the `material_slots[<index>].material` property with `CONSTANT` interpolation.
    -   **Example:**
        ```zw
        ZW-OBJECT:
          NAME: MyCharacter
          MATERIAL: DefaultSkinMat // Initial material
        ///
        ZW-MATERIAL: // Define the override material (or ensure it exists)
          NAME: EvilCorruptSkinMat
          COLOR: "#8B0000" // Dark Red
          BSDF:
            ROUGHNESS: 0.8
        ///
        ZW-STAGE:
          TRACKS:
            - TYPE: MATERIAL_OVERRIDE
              TARGET: "MyCharacter"
              MATERIAL_NAME: "EvilCorruptSkinMat"
              START_FRAME: 50
              END_FRAME: 100
              RESTORE_ON_END: "true"
        ///
        ```

6.  **`TYPE: SHADER_SWITCH`**
    -   **Purpose:** Changes and keyframes the value of a specific input socket on a shader node within an object's material.
    -   **Specific Parameters:**
        -   `TARGET: <TargetObjectNameString>`: The ZW-OBJECT whose material will be affected.
        -   `MATERIAL_NAME: <OptionalMaterialNameString>`: Name of the material to modify. If omitted, uses the object's active material or first material slot.
        -   `TARGET_NODE: <ShaderNodeNameString>`: The name of the shader node (e.g., "Principled BSDF", "MixRGB_Glow").
        -   `INPUT_NAME: <SocketNameString>`: The name of the input socket on the `TARGET_NODE` (e.g., "Roughness", "Alpha", "Base Color", "Fac").
        -   `NEW_VALUE: <ScalarOrTupleString>`: The new value for the socket. Parsed based on socket type (float, color tuple string, vector tuple string, boolean string).
        -   `FRAME: <Integer>`: The frame at which to set and keyframe this new value.
    -   **Behavior:** Locates the specified shader node input and keyframes its `default_value` with `CONSTANT` interpolation at the given `FRAME`.
    -   **Example:**
        ```zw
        ZW-OBJECT:
          NAME: MagicOrb
          MATERIAL: OrbMaterial
          COLOR: "#0000FF" // Blue
          BSDF: {ROUGHNESS: 0.1, EMISSION_STRENGTH: 1.0, EMISSION_COLOR: "#0000FF"}
        ///
        ZW-STAGE:
          TRACKS:
            - TYPE: SHADER_SWITCH
              TARGET: "MagicOrb"
              // MATERIAL_NAME: "OrbMaterial" // Optional if it's the active/first
              TARGET_NODE: "Principled BSDF"
              INPUT_NAME: "Emission Strength" // Blender socket name
              NEW_VALUE: 10.0
              FRAME: 75
            - TYPE: SHADER_SWITCH
              TARGET: "MagicOrb"
              TARGET_NODE: "Principled BSDF"
              INPUT_NAME: "Base Color"
              NEW_VALUE: "(1.0, 0.0, 0.0, 1.0)" // Switch to Red
              FRAME: 75
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

### Phase 6.9: Cameras and Lights with `ZW-CAMERA` and `ZW-LIGHT`

This phase extends the ZW protocol to support the definition and configuration of camera and light objects within Blender, essential components for rendering and scene composition.

#### ZW Syntax for Cameras (`ZW-CAMERA`):

Defines a camera object with its properties. The `blender_adapter.py` expects the ZW parser to provide the attributes for a `ZW-CAMERA` as a dictionary value if `ZW-CAMERA` is a key.

```zw
ZW-CAMERA: // This key's value should be the dictionary of attributes below
  NAME: <CameraNameString>
  LOCATION: "(x, y, z)"       // Euler angles, in degrees by ZW convention
  ROTATION: "(rx, ry, rz)"    // Euler angles, in degrees by ZW convention
  FOV: <FocalLengthFloat>     // Field of View in millimeters (e.g., 35, 50)
  CLIP_START: <Float>         // Near clipping distance
  CLIP_END: <Float>           // Far clipping distance
  TRACK_TARGET: <TargetObjectNameString> // Optional: Name of an object for a 'Track To' constraint
  COLLECTION: <CollectionNameString>   // Optional: Assign to a specific collection
///
```

-   **`NAME`**: The name for the camera object in Blender.
-   **`LOCATION`**: World-space coordinates `(x, y, z)` as a string tuple.
-   **`ROTATION`**: Euler rotation `(rx, ry, rz)` in degrees as a string tuple. The adapter converts to radians.
-   **`FOV`**: Camera lens focal length in millimeters.
-   **`CLIP_START`, `CLIP_END`**: Near and far clipping distances.
-   **`TRACK_TARGET`** (Optional): The name of an existing ZW-OBJECT that this camera should track using a 'Track To' constraint (tracks with its -Z axis, Y-axis up).
-   **`COLLECTION`** (Optional): Assigns the camera to a specific Blender collection.

#### ZW Syntax for Lights (`ZW-LIGHT`):

Defines a light object with its properties. Similar to `ZW-CAMERA`, the adapter expects the attributes as a dictionary value.

```zw
ZW-LIGHT: // This key's value should be the dictionary of attributes below
  NAME: <LightNameString>
  LOCATION: "(x, y, z)"
  ROTATION: "(rx, ry, rz)"    // Euler angles, in degrees
  TYPE: <POINT|SUN|SPOT|AREA> // Type of light
  COLOR: "<#RRGGBB>" | "(R,G,B,A)" // Light color
  ENERGY: <Float>             // Light intensity/strength
  SHADOW: "true" | "false"    // Enable or disable shadows (boolean as string)
  SIZE: <Float>               // Affects shadow softness (for POINT, SUN, SPOT) or physical size (for AREA)
  COLLECTION: <CollectionNameString>   // Optional: Assign to a specific collection
///
```

-   **`NAME`**: The name for the light object in Blender.
-   **`LOCATION`, `ROTATION`**: World-space transform, rotation in degrees (converted to radians by adapter).
-   **`TYPE`**: The type of Blender light. Supported: `POINT`, `SUN`, `SPOT`, `AREA`.
-   **`COLOR`**: Light color, specified as a hex string (e.g., `"#FFFFE0"`) or an RGBA tuple string (e.g., `"(0.7, 0.7, 1.0, 1.0)"`). Parsed by `parse_color`.
-   **`ENERGY`**: The strength or intensity of the light.
-   **`SHADOW`**: `"true"` or `"false"` (case-insensitive) to enable/disable shadows.
-   **`SIZE`**: Interpretation depends on `TYPE`:
    -   `POINT`, `SPOT`: Radius for soft shadows.
    -   `SUN`: Angular diameter for soft shadows (Blender's `angle` property).
    -   `AREA`: Physical size (e.g., for one dimension if shape is Square/Rectangle).
-   **`COLLECTION`** (Optional): Assigns the light to a specific Blender collection.

#### How it Works in `blender_adapter.py`:

-   The `process_zw_structure` function now recognizes `ZW-CAMERA` and `ZW-LIGHT` as top-level keys (or however the parser structures them based on the ZW input) and passes their attribute dictionaries to new handler functions: `handle_zw_camera_block` and `handle_zw_light_block`.
-   **`handle_zw_camera_block`**:
    -   Parses attributes, converting rotation to radians.
    -   Creates a new camera object in Blender (`bpy.ops.object.camera_add()`).
    -   Sets its name, location, and rotation.
    -   Configures camera-specific data like `lens` (FOV), `clip_start`, and `clip_end`.
    -   If `TRACK_TARGET` is specified, it finds the target object and applies a 'Track To' constraint.
    -   Assigns the camera to the specified or current collection.
-   **`handle_zw_light_block`**:
    -   Parses attributes, converting rotation to radians and color using `parse_color`.
    -   Creates a new light datablock (`bpy.data.lights.new()`) and a corresponding Blender object.
    -   Sets the light object's transform and links it to the appropriate collection.
    -   Configures light-specific data: `type`, `color`, `energy`, `use_shadow`, and `size`/`angle` based on the light type.

#### Example:

```zw
ZW-OBJECT:
  TYPE: Cube
  NAME: FocusPointCube
  LOCATION: (0,0,1)
  COLLECTION: SceneTargets
///

ZW-CAMERA:
  NAME: TrackingCam
  LOCATION: (0, -10, 2)
  ROTATION: "(0,0,0)" // Will be overridden by Track To if target found
  FOV: 80
  TRACK_TARGET: FocusPointCube
  COLLECTION: Cameras
///

ZW-LIGHT:
  NAME: MainSun
  LOCATION: (5, 5, 5)
  ROTATION: "(45,0,45)"
  TYPE: SUN
  COLOR: "#FFF5E1" // Warm white
  ENERGY: 2.0
  SIZE: 0.05 // Small angle for sharper sun shadows
  SHADOW: "true"
  COLLECTION: Lights
///
```

This addition allows ZW to define not just the subjects of a scene, but also how they are viewed and illuminated, completing a more comprehensive scene description toolset.

### Phase 6.10: Procedural Meshes with `ZW-MESH` (UVs, Textures, Export)

This phase introduces the `ZW-MESH:` block, allowing for the definition of 3D meshes through a procedural pipeline. This involves specifying a base primitive, a series of deformations, and material properties, all processed by a dedicated Python module (`zw_mesh.py`) called by the main `blender_adapter.py`.

#### ZW Syntax for Procedural Meshes (`ZW-MESH`):

A `ZW-MESH:` block defines a complete procedural mesh object. The `blender_adapter.py` expects the ZW parser to provide the attributes for a `ZW-MESH` as a dictionary value if `ZW-MESH` is the key.

```zw
ZW-MESH: // This key's value should be the dictionary of attributes below
  NAME: <UniqueObjectNameString>
  TYPE: <BasePrimitiveTypeString> // e.g., "ico_sphere", "cylinder", "grid", "cube", "cone"
                                  // (Note: `zw_mesh.py` might also check for a 'BASE' key)
  PARAMS:                         // Dictionary of parameters for the base primitive
    SUBDIVISIONS: <Integer>       // (for ico_sphere)
    RADIUS: <Float>               // (for ico_sphere, cylinder)
    VERTICES: <Integer>           // (for cylinder, cone)
    DEPTH: <Float>                // (for cylinder, cone)
    X_SUBDIVISIONS: <Integer>     // (for grid)
    Y_SUBDIVISIONS: <Integer>     // (for grid)
    SIZE: <Float>                 // (for grid, cube)
    // ... other primitive-specific params ...
  DEFORMATIONS:                   // Optional list of deformation operations to apply sequentially
    - TYPE: <DeformationTypeString> // e.g., "twist", "displace", "skin"
      // ... parameters specific to this deformation type ...
      AXIS: <X|Y|Z>
      ANGLE: <FloatInDegrees>     // (for twist)
      TEXTURE: <TextureTypeString>  // (e.g., "noise" for displace, maps to Blender types like "CLOUDS")
      STRENGTH: <Float>           // (for displace)
      THICKNESS: <Float>          // (for skin)
    // ... more deformations ...
  MATERIAL:                       // Optional dictionary defining the object's material
    NAME: <MaterialNameString>    // Optional: name for the material in Blender
    BASE_COLOR: "<#RRGGBB>" | "(R,G,B,A)"
    EMISSION: <Float>             // Emission strength
    EMISSION_COLOR: "<#RRGGBB>" | "(R,G,B,A)" // Optional: color for emission
    TEXTURE:                      // Optional: Texture definition for the material
      TYPE: <image|noise|etc.>   // Type of texture
      FILE: "<path/to/image.png>" // (For TYPE: image) Path to image file, relative to project root
      MAPPING: <UV|GENERATED|etc.> // (For TYPE: image, optional) Default: UV
      SCALE: "(u,v)"              // (For TYPE: image, optional) UV scale as string tuple, e.g., "(2.0, 2.0)"
      STRENGTH: <Float>           // (For TYPE: noise, optional) Strength/influence of noise
      TEX_SCALE: <Float>          // (For TYPE: noise, optional) Scale of the noise texture itself
    // ... other BSDF params from Phase 6.3 could be nested here if `zw_mesh.py` supports them ...
  LOCATION: "(x, y, z)"           // Optional: World-space location
  ROTATION: "(rx, ry, rz)"        // Optional: Euler rotation in degrees
  SCALE: "(sx, sy, sz)"           // Optional: Scale factors
  COLLECTION: <CollectionNameString> // Optional: Assign to a specific collection
  EXPORT:                         // Optional: Export definition for this mesh
    FORMAT: <glb|obj|etc.>        // File format for export (currently 'glb' supported)
    FILE: "<path/to/export_file>" // Output filepath, relative to project root (e.g., "exports/my_mesh.glb")
///
```

-   **`NAME`**: The name for the final Blender object.
-   **`TYPE`** (or **`BASE`**): Specifies the base primitive mesh (e.g., "ico_sphere", "cylinder", "grid", "cube", "cone"). The `zw_mesh.py` module's `create_base_mesh` function handles this.
-   **`PARAMS`**: A dictionary of parameters for the chosen base primitive (e.g., `RADIUS`, `SUBDIVISIONS`, `DEPTH`, `VERTICES`, `SIZE`).
-   **`DEFORMATIONS`** (Optional): A list of dictionaries, each defining a deformation to be applied sequentially.
    -   `TYPE`: The kind of deformation (e.g., "twist", "displace", "skin" - initial supported types in `zw_mesh.py`).
    -   Other keys within each deformation dictionary are parameters for that specific deformation type (e.g., `AXIS`, `ANGLE` for twist; `TEXTURE`, `STRENGTH` for displace).
-   **`MATERIAL`** (Optional): A dictionary defining the material properties.
    -   `NAME` (Optional): Name for the Blender material.
    -   `BASE_COLOR`: Hex string or tuple string.
    -   `EMISSION`: Emission strength (float).
    -   `EMISSION_COLOR` (Optional): Color for emission.
    -   `TEXTURE` (Optional): A dictionary defining a texture to be applied to the material.
        -   `TYPE`: Specifies the texture type (e.g., `"image"`, `"noise"`).
        -   `FILE` (for `TYPE: "image"`): Path to the image file (e.g., `"assets/textures/my_texture.png"`).
        -   `MAPPING` (for `TYPE: "image"`, Optional): Texture mapping method. `"UV"` implies automatic UV unwrapping (Smart UV Project) will be attempted if image texture is used. Defaults to `"UV"`.
        -   `SCALE` (for `TYPE: "image"`, Optional): UV mapping scale as a string tuple `"(u,v)"`.
        -   `STRENGTH`, `TEX_SCALE` (for `TYPE: "noise"`, Optional): Parameters for procedural noise texture.
    -   (Future: Could support a full `BSDF` block here if `zw_mesh.py`'s `apply_material` is expanded).
-   **`LOCATION`, `ROTATION`, `SCALE`** (Optional): Standard transform attributes. Rotation is in degrees.
-   **`COLLECTION`** (Optional): Assigns the created mesh object to a specific Blender collection.
-   **`EXPORT`** (Optional): A dictionary defining export parameters for this mesh.
    -   `FORMAT`: The desired file format (e.g., `"glb"`). Currently, only "glb" is supported.
    -   `FILE`: The output file path (e.g., `"exports/my_model.glb"`), typically relative to the project root.

#### How it Works in `blender_adapter.py` and `zw_mesh.py`:

-   The `process_zw_structure` function in `blender_adapter.py` now recognizes `ZW-MESH` keys.
-   It calls `handle_zw_mesh_block(mesh_definition_dict, current_bpy_collection)` which is imported from the new `zw_mcp/zw_mesh.py` module.
-   The `zw_mesh.handle_zw_mesh_block` function then orchestrates:
    1.  Calling `zw_mesh.create_base_mesh()` to generate the initial primitive in Blender based on `TYPE` and `PARAMS`.
    2.  Setting the object's `NAME`, `LOCATION`, `ROTATION`, and `SCALE`.
    3.  Before applying materials, if an image texture with UV mapping is specified in the `TEXTURE` block, it calls `add_uv_mapping(created_obj)` to perform a Smart UV Project.
    4.  If `DEFORMATIONS` are present, iterating through them and calling `zw_mesh.apply_deformations()` (which in turn calls specific helpers like `add_twist_deform`, `add_displace_deform`, `add_skin_deform` to add and configure Blender modifiers).
    5.  If `MATERIAL` is defined, calling `zw_mesh.apply_material()` (which calls `apply_texture_to_material_nodes`) now handles the `TEXTURE` block by creating and connecting appropriate shader nodes (Image Texture with UV/Mapping setup, or Noise Texture) to the Principled BSDF's Base Color input.
    6.  Linking the final object to the appropriate Blender collection (passed as `current_bpy_collection` or determined by an explicit `COLLECTION` attribute in the `ZW-MESH` block).
    7.  Includes error handling, creating a fallback "error cube" if the process fails.
    8.  After all other processing, if an `EXPORT` block is present, it calls `export_to_glb(created_obj, export_filepath)` to save the object as a GLB file.

#### Example (`Crystalline_Stone`):

```zw
// --- Test Case for ZW-MESH with Texture and Export (Phase 8.6) ---
ZW-MESH:
  NAME: Crystalline_Stone
  TYPE: cylinder
  PARAMS:
    VERTICES: 12
    RADIUS: 0.8
    DEPTH: 2.5
  DEFORMATIONS:
    - TYPE: displace
      TEXTURE: noise
      STRENGTH: 0.2
  MATERIAL:
    NAME: StoneMat
    BASE_COLOR: "#CCCCCC"
    EMISSION: 0.1
    TEXTURE:
      TYPE: image
      FILE: "assets/textures/stone_diffuse.png"
      MAPPING: UV
      SCALE: "(1.5, 1.5)"
  LOCATION: "(2.0, 0.0, 1.25)"
  ROTATION: "(0,0,0)"
  SCALE: "(1,1,1)"
  COLLECTION: ProceduralAssets
  EXPORT:
    FORMAT: glb
    FILE: "exports/crystalline_stone.glb"
///
```

This `ZW-MESH` system forms the foundation for a powerful procedural geometry pipeline driven by ZW, enabling complex shapes and objects to be generated from structured text descriptions. The `zw_mesh.py` module now supports icospheres, cylinders, grids, cubes, and cones as base meshes; twist, displace, and skin deformations; material application including image and procedural noise textures with UV unwrapping for image textures; and exporting the final mesh to GLB format.

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

---
## Phase 8.0: Scene Composition via `ZW-STAGE` (Initial Implementation)

This phase introduces the `ZW-STAGE` block, enabling timeline-based orchestration of scene elements and events within Blender. It allows for sequencing camera switches, object visibility changes, and light animations, forming the foundation for more complex cinematic and narrative control directly from ZW.

### ZW Syntax for Staging (`ZW-STAGE`):

A `ZW-STAGE` block defines a sequence of events or states over time using a list of "tracks".

```zw
ZW-STAGE:
  NAME: <OptionalStageName> // A descriptive name for this stage or sequence
  TRACKS:                  // A list of track definitions
    - TYPE: <TrackTypeString>
      TARGET: <TargetObjectNameString>
      START: <StartFrameInteger>
      END: <OptionalEndFrameInteger> // Meaning varies by track type
      // ... other parameters specific to the TrackType ...
    // ... more tracks ...
///
```

-   **`NAME`** (Optional): An identifier for the stage.
-   **`TRACKS`**: A list of dictionaries, where each dictionary defines a single timed event or state change.

#### Common Track Parameters:

-   **`TYPE`**: A string identifying the kind of event (e.g., "CAMERA", "VISIBILITY", "LIGHT_INTENSITY").
-   **`TARGET`**: The `NAME` of the ZW-defined Blender object, camera, or light that this track affects.
-   **`START: <Integer>`**: The frame number at which this track event begins or is set.
-   **`END: <Integer>`** (Optional): The frame number at which an event might end or transition. Its usage is specific to the `TYPE`.

#### Initially Supported Track Types:

1.  **`TYPE: CAMERA`**
    -   **Purpose:** Sets the active scene camera.
    -   **Specific Parameters:**
        -   `TARGET`: Name of a `ZW-CAMERA` object.
    -   **Behavior:** At the `START` frame, `bpy.context.scene.camera` is set to the specified target camera, and a keyframe is inserted for this property.
        *(Note: For this initial pass, if multiple CAMERA tracks exist, the one with the latest `START` frame before or at the current frame during playback will effectively be active. True "duration" for a camera shot might involve more complex NLA/marker setups in future enhancements).*
    -   **Example:**
        ```zw
        ZW-STAGE:
          TRACKS:
            - TYPE: CAMERA
              TARGET: "MainOverviewCam"
              START: 1
            - TYPE: CAMERA
              TARGET: "PlayerCloseUpCam"
              START: 150
        ///
        ```

2.  **`TYPE: VISIBILITY`**
    -   **Purpose:** Controls the viewport and render visibility of an object.
    -   **Specific Parameters:**
        -   `TARGET`: Name of a `ZW-OBJECT`.
        -   `STATE: "SHOW" | "HIDE"`: Determines whether to make the object visible or hidden.
    -   **Behavior:** At the `START` frame, the `target_obj.hide_viewport` and `target_obj.hide_render` properties are keyframed according to the `STATE` (`hide_viewport = False` for "SHOW", `True` for "HIDE").
    -   **Example:**
        ```zw
        ZW-STAGE:
          TRACKS:
            - TYPE: VISIBILITY
              TARGET: "SecretTreasure"
              START: 1
              STATE: "HIDE"
            - TYPE: VISIBILITY
              TARGET: "SecretTreasure"
              START: 200
              STATE: "SHOW"
        ///
        ```

3.  **`TYPE: LIGHT_INTENSITY`**
    -   **Purpose:** Animates the energy (intensity) of a light.
    -   **Specific Parameters:**
        -   `TARGET`: Name of a `ZW-LIGHT` object.
        -   `VALUE: <Float>`: The light's energy value to be set at the `START` frame.
        -   `END_VALUE: <Float>` (Optional): If provided along with an `END` frame, the energy will be animated from `VALUE` (at `START`) to `END_VALUE` (at `END`). If `END_VALUE` is omitted, the energy is simply set to `VALUE` at `START`.
        -   `END: <Integer>` (Optional): The frame at which `END_VALUE` should be reached.
    -   **Behavior:** Keyframes are inserted for the `target_obj.data.energy` property at the `START` frame (with `VALUE`) and, if `END` and `END_VALUE` are provided, at the `END` frame (with `END_VALUE`).
    -   **Example:**
        ```zw
        ZW-LIGHT:
          NAME: MySpotlight
          TYPE: SPOT
          ENERGY: 100
        ///
        ZW-STAGE:
          TRACKS:
            - TYPE: LIGHT_INTENSITY
              TARGET: "MySpotlight"
              START: 10
              VALUE: 500 // Brighten at frame 10
            - TYPE: LIGHT_INTENSITY
              TARGET: "MySpotlight"
              START: 50
              VALUE: 1500 // Brighten further
              END: 100
              END_VALUE: 0 // Fade to black by frame 100
        ///
        ```

#### How it Works in `blender_adapter.py`:

-   The `process_zw_structure` function now recognizes `ZW-STAGE` keys and passes the associated dictionary to a new `handle_zw_stage_block` function.
-   `handle_zw_stage_block` iterates through the `TRACKS` list.
-   For each track, it identifies the `TYPE` and calls specific logic to:
    -   Find the target Blender entity (object, camera, light).
    -   Set and keyframe the appropriate Blender properties at the specified `START` (and `END` if applicable) frames. For instance, for `VISIBILITY`, it keyframes `hide_viewport` and `hide_render`. For `LIGHT_INTENSITY`, it keyframes `light.data.energy`. For `CAMERA`, it keyframes `scene.camera`.

This initial implementation of `ZW-STAGE` provides a foundational system for scripting basic timeline events and scene dynamics using the ZW protocol.

---
## ZW Tools: Utility & R&D Lab Scripts

This section covers utility scripts that support the development, testing, and management of ZW files and the ZW MCP ecosystem. These tools are typically run standalone and are not part of the core runtime libraries like `blender_adapter.py` or `ollama_agent.py`.

### `tools/zw_import_watcher.py`

-   **Purpose:** Monitors a specified local folder for new `.zw` (ZW Template) files, performs a basic validation check on them, and then sorts them into a "validated" folder or logs them as "rejected". This script is intended as a utility for research and development, helping to manage incoming ZW patterns or templates before they are formally integrated or used by more complex parts of the system.
-   **Functionality:**
    -   **Monitored Folder:** `zw_drop_folder/experimental_patterns/` (relative to the project root where the script is ideally run, or where `zw_drop_folder` is created).
    -   **Validation (Placeholder):** The current validation logic in `validate_zw_template()` is a placeholder. It first checks if a file contains the line "ENTROPY:" (as per an earlier user specification for a particular template type). If not found, as a fallback for more general ZW files, it checks for the presence of common ZW structural tags such as "ZW-OBJECT:", "TYPE:", "ZW-STAGE:", "ZW-CAMERA:", "ZW-LIGHT:", "ZW-FUNCTION:", "ZW-DRIVER:", or "ZW-ANIMATION:". A file is considered valid if either the "ENTROPY:" line or at least one of the basic structural tags is detected. This function is intended to be replaced or augmented with calls to a more robust ZW schema validator or the `zw_parser.validate_zw()` function as the ZW protocol matures.
    -   **Output Folders:**
        -   Valid files are copied to `zw_drop_folder/validated_patterns/`.
        -   A log of all processed files (both validated and rejected) with timestamps and validation messages is appended to `zw_drop_folder/research_notes/what_worked.md`.
    -   **Operation:** The script continuously polls the watch folder every 3 seconds. It keeps track of files it has already seen in the current session to only process new additions.
    -   **Directory Setup:** On startup, the script will attempt to create the `WATCH_FOLDER`, `VALIDATED_FOLDER`, and the directory for `RESEARCH_LOG` (`zw_drop_folder/research_notes/`) if they don't already exist. These paths are rooted in a `zw_drop_folder` created at the project root level.

-   **How to Run:**
    1.  Navigate to the root directory of the ZW MCP project in your terminal.
    2.  Ensure the `tools/` directory and `zw_import_watcher.py` script are present.
    3.  Run the script using Python:
        ```bash
        python tools/zw_import_watcher.py
        ```
    4.  The script will start monitoring the `zw_drop_folder/experimental_patterns/` directory.
    5.  To stop the watcher, press `Ctrl+C` in the terminal where it's running.

-   **Expected Directory Structure for Operation (created by the script if not present, relative to project root):**
    ```
    zw_drop_folder/
    ├── experimental_patterns/   # Drop new .zw files here
    ├── validated_patterns/      # Valid .zw files are copied here
    └── research_notes/
        └── what_worked.md       # Log of processing results
    ```

-   **Note:** This script is primarily for development and pattern management workflows. The paths and validation logic are currently hardcoded but could be made configurable in future versions. Internally, it uses `pathlib` for robust cross-platform path management and ensures UTF-8 encoding for file operations.

---
## Phase 9.0: Scene Assembly with `ZW-COMPOSE` (Foundation)

This phase introduces the `ZW-COMPOSE` block, a powerful directive that allows for the assembly of complex objects or entire scenes by referencing, instancing, transforming, and overriding materials of pre-defined ZW components (created via `ZW-OBJECT` or `ZW-MESH`). This facilitates modular design and is a key step towards AI-driven scene construction where an AI can generate a `ZW-COMPOSE` block to build scenes from a library of parts or procedural elements.

### ZW Syntax for Scene Composition (`ZW-COMPOSE`):

A `ZW-COMPOSE` block defines an assembly, typically resulting in a new parent Empty object in Blender that holds all the composed parts.

```zw
ZW-COMPOSE:
  NAME: <CompositionNameString>     // Name for the parent Empty of the assembly
  LOCATION: "(x, y, z)"            // Optional: Location for the parent Empty
  ROTATION: "(rx, ry, rz)"         // Optional: Rotation for the parent Empty (degrees)
  SCALE: "(sx, sy, sz)"            // Optional: Scale for the parent Empty
  COLLECTION: <CollectionNameString> // Optional: Collection for the parent Empty

  BASE_MODEL: <ZW_EntityNameString>  // NAME of a ZW-OBJECT or ZW-MESH to use as the base

  ATTACHMENTS:                      // Optional: List of parts to attach to the base/parent
    - OBJECT: <ZW_EntityNameString> // NAME of a ZW-OBJECT or ZW-MESH to attach
      LOCATION: "(x, y, z)"        // Optional: Local position relative to the parent Empty
      ROTATION: "(rx, ry, rz)"     // Optional: Local rotation (degrees)
      SCALE: "(sx, sy, sz)"        // Optional: Local scale
      MATERIAL_OVERRIDE:           // Optional: Override material for this attached instance
        NAME: <NewMaterialName>
        BASE_COLOR: "<#RRGGBB>" | "(R,G,B,A)"
        EMISSION: <Float>
        EMISSION_COLOR: "<#RRGGBB>" | "(R,G,B,A)"
        // Potentially full BSDF or TEXTURE block here in future
    // ... more attachments ...

  EXPORT:                           // Optional: Export the entire composed assembly
    FORMAT: glb
    FILE: "exports/<filename>.glb"
///
```

-   **`NAME`**: The name for the top-level parent Empty object that will hold the entire assembly.
-   **`LOCATION`, `ROTATION`, `SCALE`** (Optional, for the main assembly): Transform for the parent Empty. Rotations are in degrees.
-   **`COLLECTION`** (Optional, for the main assembly): Collection for the parent Empty.
-   **`BASE_MODEL`**: The `NAME` of a previously defined `ZW-OBJECT` or `ZW-MESH` that serves as the central part of the composition.
-   **`ATTACHMENTS`**: A list of dictionaries, each defining an object to be attached:
    -   `OBJECT`: The `NAME` of a previously defined `ZW-OBJECT` or `ZW-MESH`.
    -   `LOCATION`, `ROTATION`, `SCALE` (Optional): Local transforms applied to this attachment, relative to the main assembly's parent Empty. Rotations are in degrees.
    -   `MATERIAL_OVERRIDE` (Optional): A dictionary (similar in structure to the `MATERIAL` block in `ZW-MESH`) to define a unique material appearance for this specific attached instance.
-   **`EXPORT`** (Optional): If present, exports the entire assembled group (the parent Empty and all its children) to the specified format and file. Currently supports `FORMAT: glb`.

### How it Works in `blender_adapter.py`:

-   The `process_zw_structure` function now recognizes `ZW-COMPOSE` keys.
-   It calls `handle_zw_compose_block(compose_data_dict, current_bpy_collection)`:
    1.  Creates a new parent Empty object in Blender, named and transformed according to the `ZW-COMPOSE` block's `NAME`, `LOCATION`, `ROTATION`, and `SCALE`. This Empty is linked to the specified or current collection.
    2.  **Base Model Processing**:
        -   Finds the Blender object corresponding to the `BASE_MODEL` name.
        -   Duplicates this object (including its mesh data, making it independent for this composition).
        -   Parents the duplicated base model to the main parent Empty and resets its local transforms (so its world position is initially that of the Empty).
    3.  **Attachment Processing**:
        -   For each item in the `ATTACHMENTS` list:
            -   Finds the Blender object for the specified `OBJECT` name.
            -   Duplicates it (including mesh data).
            -   Parents the duplicated attachment to the main parent Empty.
            -   Applies the local `LOCATION`, `ROTATION` (converted to radians), and `SCALE` from the attachment definition to this new instance.
            -   If a `MATERIAL_OVERRIDE` is defined, the `apply_material` function (from `zw_mesh.py`, or a similar utility) is used to apply these specific material properties to this instance of the attachment.
    4.  **Export**: If an `EXPORT` block is present:
        -   Selects the main parent Empty and all its children recursively.
        -   Uses `bpy.ops.export_scene.gltf()` to export the selected hierarchy to a `.glb` file.

### Example (`CrystalShrine_Assembly`):

First, ensure these `ZW-MESH` components are defined earlier in your `.zw` file:
```zw
ZW-MESH:
  NAME: Base_Shrine
  TYPE: cylinder
  PARAMS: {VERTICES: 24, RADIUS: 2.0, DEPTH: 0.6}
  MATERIAL: {NAME: ShrineStoneMat, BASE_COLOR: "#8B8B8B", EMISSION: 0.05}
  COLLECTION: ShrineParts
///
ZW-MESH:
  NAME: Crystal_Top
  TYPE: ico_sphere
  PARAMS: {SUBDIVISIONS: 2, RADIUS: 0.5}
  MATERIAL: {NAME: CrystalMat, BASE_COLOR: "#A3FFD3", EMISSION: 1.2}
  COLLECTION: ShrineParts
///
ZW-MESH:
  NAME: Side_Shard
  TYPE: cone
  PARAMS: {VERTICES: 8, RADIUS1: 0.15, RADIUS2: 0.0, DEPTH: 0.7}
  MATERIAL: {NAME: ShardMat, BASE_COLOR: "#00FFFF", EMISSION: 0.7}
  COLLECTION: ShrineParts
///
```
Then, the `ZW-COMPOSE` block can assemble them:
```zw
ZW-COMPOSE:
  NAME: CrystalShrine_Assembly
  BASE_MODEL: Base_Shrine
  LOCATION: "(0, 15, 0)"
  ROTATION: "(0,0,15)"
  COLLECTION: ComposedScenes
  ATTACHMENTS:
    - OBJECT: Crystal_Top
      LOCATION: "(0.0, 0.0, 0.5)"
      ROTATION: "(0.0, 0.0, 0.0)"
      SCALE: "(1.0, 1.0, 1.0)"
    - OBJECT: Side_Shard
      LOCATION: "(1.2, 0.0, 0.3)"
      ROTATION: "(0.0, 90, 10)"
      SCALE: "(0.8, 0.8, 1.0)"
      MATERIAL_OVERRIDE:
        NAME: OverriddenShardMat
        BASE_COLOR: "#FF66CC"
        EMISSION: 1.5
  EXPORT:
    FORMAT: glb
    FILE: "exports/crystal_shrine_assembly.glb"
///
```

This `ZW-COMPOSE` feature allows for building complex, hierarchical models from smaller, reusable ZW components, and is a key enabler for more sophisticated AI-driven design and scene generation.

[end of README.md]
