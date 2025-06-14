# ZW MCP Ecosystem: AI-Powered Creative Orchestration

![ZW MCP System Diagram](https://via.placeholder.com/800x400?text=ZW+MCP+System+Architecture)
*A unified framework for AI-assisted content creation, 3D modeling, and narrative generation*

## Overview

ZW MCP is an advanced ecosystem that bridges AI-powered language models with creative tools through the ZW protocol - a structured format for describing scenes, animations, and narratives. This system enables:

- 🧠 **AI-assisted creation** using Ollama language models
- 🎨 **Procedural 3D content generation** in Blender
- 🤖 **Multi-agent collaboration** for complex tasks
- 🔄 **Roundtrip workflows** between text and 3D environments
- ⚡ **Real-time networked communication** between components

 ollama-mcp-phase2-daemon

### Core Components
| Component | Purpose | Key Technologies |
|-----------|---------|------------------|
| **ZW MCP Daemon** | Networked API endpoint | Python, TCP Socket |
| **Ollama Handler** | AI communication layer | REST API, JSON |
| **ZW Parser** | Protocol validation/translation | Python, Regex |
| **Autonomous Agents** | AI-powered task execution | State machines, Memory |
| **Blender Adapter** | 3D content generation | bpy, Geometry Nodes |

### Advanced Capabilities
- **Multi-Agent Orchestration**
  ```mermaid
  graph LR
    A[Master Seed] --> B[Agent 1]
    B --> C[Agent 2]
    C --> D[Agent 3]
    D --> E[Final Output]
  ```
- **Procedural 3D Generation**
  - Object hierarchies with parenting
  - Material/shader configuration
  - Geometry node operations
  - Keyframe animation system

- **Networked Services**
  - TCP daemon (port 7421)
  - Client/server architecture
  - Session logging/monitoring

## Getting Started

### Prerequisites
- Python 3.9+
- [Ollama](https://ollama.ai/) (local instance)
- Blender 3.0+
- Required packages: `pip install requests numpy`

<<<<<<< HEAD
### Installation
```bash
git clone https://github.com/SmokesBowls/zw_mcp.git
cd zw_mcp
conda create -n zw_env python=3.10
conda activate zw_env
pip install -r requirements.txt
```

### Basic Usage
1. Start the TCP daemon:
```bash
python zw_mcp/zw_mcp_daemon.py
```

2. Send a ZW prompt:
```bash
python zw_mcp/client_example.py prompts/example.zw
```
=======
- Python 3
- `requests` library (`pip install requests`)
- A running local Ollama instance.

### Usage (`zw_mcp_server.py`)

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

    To simply process an input file and print to console:
    ```bash
    python3 zw_mcp/zw_mcp_server.py zw_mcp/prompts/example.zw
    ```

---
>>>>>>> ollama-mcp-phase2-daemon

3. Generate 3D content in Blender:
```bash
blender --background --python zw_mcp/blender_adapter.py
```

<<<<<<< HEAD
## System Architecture
=======
This phase transforms the ZW MCP into a network-accessible service, allowing other tools and applications to interact with it over TCP.

### New Scripts for Phase 2

- **`zw_mcp/zw_mcp_daemon.py`**:
    - A TCP server that listens for incoming ZW-formatted prompts on a configurable host and port (default: `127.0.0.1:7421`).
    - Handles multiple client connections concurrently using threading.
    - Receives multi-line ZW input (terminated by `///`).
    - Uses `ollama_handler.py` to query the Ollama API.
    - Sends Ollama's response back to the connected client.
    - Logs all incoming prompts and their corresponding responses to `zw_mcp/logs/daemon.log`.
- **`zw_mcp/client_example.py`**:
    - An example CLI client to test and interact with the `zw_mcp_daemon.py`.

### How to Use the TCP Daemon

1.  **Start the ZW MCP Daemon:**
    ```bash
    python3 zw_mcp/zw_mcp_daemon.py
    ```
2.  **Run the Example Client (or your own tool):**
    ```bash
    python3 zw_mcp/client_example.py path/to/your/prompt.zw
    ```

This networked setup allows various external applications to interface with the ZW MCP and, by extension, with Ollama.

---
## Overall Project Directory Structure (as of Phase 9.1)

This provides a more holistic view of the key components and where to find them. Older tools are listed at the end for completeness.
>>>>>>> ollama-mcp-phase2-daemon

### Core Components
```
zw_mcp/
<<<<<<< HEAD
├── core/                 # Central services
│   ├── daemon.py         # TCP server
│   ├── ollama_handler.py # AI communication
│   └── zw_parser.py      # Protocol handling
├── agents/               # Autonomous agents
│   ├── orchestrator.py   # Multi-agent control
│   └── profiles/         # Agent configurations
├── adapters/             # Software integrations
│   └── blender/          # Blender 3D adapter
├── resources/            # Templates and assets
│   ├── prompts/          # ZW input files
│   └── schemas/          # Protocol definitions
└── tools/                # Utilities
    ├── exporter.py       # Blender→ZW conversion
    └── watcher.py        # Directory monitoring
=======
├── zw_mcp_daemon.py        # TCP Daemon server for ZW message passing
├── ollama_handler.py       # Handles API requests to Ollama
├── zw_parser.py            # ZW parsing and formatting utilities
├── test_zw_parser.py       # Unit tests for zw_parser

├── blender_adapter.py      # Script to run within Blender to interpret ZW for scene creation
├── blender_exporter.py     # Script to run within Blender to export scenes to ZW
├── zw_mesh.py              # Module for procedural mesh generation in Blender, used by blender_adapter

├── handlers/                 # Core logic handlers
│   └── template_engine.py    # ZWTemplateEngine and ZWMetadataRegistry

├── smart_assembler.py      # CLI tool for template-based scene assembly

├── agents/                   # Agent configurations (for multi-agent hub)
│   ├── narrator_config.json
│   └── historian_config.json
├── agent_runtime/            # (Created dynamically) Per-agent logs & memory
│   # ... e.g., narrator.log, narrator_memory.json ...

├── prompts/                  # ZW seed prompts and examples
│   ├── example.zw
│   ├── blender_scene.zw      # Example for blender_adapter.py
│   ├── master_seed.zw        # For zw_agent_hub.py
│   # ... other specific agent seed prompts ...
├── templates/                # Definitions for ZW-COMPOSE-TEMPLATE
│   └── altar_template.zw     # Example template
├── mesh/                     # Library of ZW component parts with METADATA
│   ├── structural_parts.zw
│   └── crystal_parts.zw

├── responses/                # Default output for some older CLI tools
└── logs/                     # General logging directory
    ├── agent.log             # Log for standalone ollama_agent.py
    ├── daemon.log            # Log for TCP daemon interactions
    ├── memory.json           # Memory for standalone ollama_agent.py
    # ... other logs ...

# Foundational Agent/Hub Components (referenced or used by more advanced systems)
├── ollama_agent.py         # Standalone autonomous agent script (also provides logic for hub agents)
├── agent_config.json       # Default config for standalone ollama_agent.py
├── zw_agent_hub.py         # Orchestrator for multi-agent sessions
├── agent_profiles.json     # Configuration for zw_agent_hub.py

# Older/Legacy CLI Tools (may still be functional or referenced)
├── zw_mcp_server.py        # Original CLI tool for direct Ollama interaction
├── client_example.py       # Example TCP client for zw_mcp_daemon.py
>>>>>>> ollama-mcp-phase2-daemon
```

### Workflow Diagram
```mermaid
sequenceDiagram
    participant User
    participant AgentHub
    participant ZWDaemon
    participant Ollama
    participant Blender

<<<<<<< HEAD
    User->>AgentHub: Initiate workflow
    AgentHub->>ZWDaemon: Send ZW prompt
    ZWDaemon->>Ollama: Request generation
    Ollama->>ZWDaemon: Return ZW response
    ZWDaemon->>Blender: Create 3D scene
    Blender->>AgentHub: Return result
    AgentHub->>User: Final output
```
=======
## Phase 2.5: ZW Autonomous Agent (Step 2: Looping Agent with Memory)

This phase enhances the autonomous agent with conversational looping, response chaining, stop-word detection, and persistent memory.

### Agent Files & Configuration

- **`zw_mcp/agent_config.json`**: Configuration for the agent.
- **`zw_mcp/ollama_agent.py` (Looping Version)**: The Python script for the autonomous agent, now with iterative capabilities.

Key settings for Step 2 in `agent_config.json`:
- `prompt_path`: Path to the **initial** ZW prompt file for the first round.
- `max_rounds`: Maximum number of conversational rounds.
- `stop_keywords`: List of strings to stop the agent's loop.
- `log_path`: File path for logging each round.
- `memory_enabled`, `memory_path`: Settings for persistent conversational memory.
- `prepend_previous_response`: If true, the previous response becomes the next prompt.

### How to Use the Looping Agent

1.  Ensure the ZW MCP Daemon (`zw_mcp_daemon.py`) is running.
2.  Configure `zw_mcp/agent_config.json`.
3.  Run the agent: `python3 zw_mcp/ollama_agent.py`.
>>>>>>> ollama-mcp-phase2-daemon

## Advanced Features

<<<<<<< HEAD
### Multi-Agent Collaboration
Configure agent teams in `agents/profiles.json`:
```json
[
  {
    "name": "Narrator",
    "config": "agents/narrator.json",
    "memory": "narrator_memory.db"
  },
  {
    "name": "Designer",
    "config": "agents/designer.json",
    "memory": "designer_memory.db"
  }
]
```

### Blender Integration Examples
**Create a material:**
```zw
ZW-MATERIAL:
  NAME: Emerald
  COLOR: "#50C878"
  ROUGHNESS: 0.2
  METALLIC: 0.8
```

**Animate an object:**
```zw
ZW-ANIMATION:
  TARGET: "Orb"
  PROPERTY: rotation
  KEYFRAMES:
    - FRAME: 0
      VALUE: (0, 0, 0)
    - FRAME: 100
      VALUE: (0, 0, 360)
```

## Development Roadmap

### Current Features
- [x] ZW protocol parser/validator
- [x] TCP networking layer
- [x] Ollama API integration
- [x] Blender scene generation
- [x] Multi-agent orchestration

### Planned Features
- [ ] Godot engine integration
- [ ] Web-based control interface
- [ ] Versioned memory system
- [ ] Physics simulation support
- [ ] Audio-reactive animations

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a pull request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

SmokesBowls - [@YourTwitter](https://twitter.com/yourhandle) - email@example.com

Project Link: [https://github.com/SmokesBowls/zw_mcp](https://github.com/SmokesBowls/zw_mcp)

---

```python
# Example Agent Configuration
AGENT_CONFIG = {
    "style": "You are an architectural designer specializing in futuristic structures",
    "memory": {
        "enabled": True,
        "depth": 5,
        "path": "memory/designer.json"
    },
    "parameters": {
        "creativity": 0.7,
        "detail_level": "high",
        "preferred_materials": ["carbon_fiber", "neoprene"]
    }
}
```

**Ready to create?** Start with our [Quickstart Guide](docs/QUICKSTART.md) or explore the [Example Gallery](examples/).
=======
---
## Phase 2.6: Memory-Driven Agent Personality

This step refines the ZW Autonomous Agent by allowing its initial prompt to be dynamically constructed based on a defined **style** and a **seed of recent memories**.

#### Key Functional Changes in `ollama_agent.py` for Personality:

- **Composite Initial Prompt:** If `use_memory_seed` is enabled in `agent_config.json`, the agent calls `build_composite_prompt()` to construct the first prompt.
- **`build_composite_prompt()` Function:** Prepends `ZW-AGENT-STYLE` and `ZW-MEMORY-SEED` blocks (with recent responses from memory) to the original seed prompt.

#### New Configuration Fields in `agent_config.json` for Personality:

- **`"style"`**: A string defining the persona or role for the agent.
- **`"use_memory_seed"`**: Boolean to enable/disable memory seeding in the initial prompt.
- **`"memory_limit"`**: Integer specifying how many recent memory entries to include.

This memory-driven personality makes the agent's initial interaction more contextually aware and stylistically aligned.
```

---
## Phase 3: ZW Parser + Validator

This phase introduces `zw_mcp/zw_parser.py`, for parsing, validating, and manipulating ZW-formatted text.

### Module: `zw_mcp/zw_parser.py`

#### Key Functions:

-   **`parse_zw(zw_text: str) -> dict`**: Converts ZW text to a nested Python dictionary.
-   **`to_zw(d: dict, current_indent_level: int = 0) -> str`**: Converts a dictionary back to ZW text.
-   **`validate_zw(zw_text: str) -> bool`**: Basic structural validation.
-   **`prettify_zw(zw_text: str) -> str`**: Cleans up and standardizes ZW text formatting.

### Testing the Parser

Run `python3 zw_mcp/test_zw_parser.py` to see demonstrations and verify functionality.

This parser is key for reliable ZW-based applications, enabling validation, normalization, and data transformation.
```

---
## Phase 5: Multi-Agent Control Framework

This phase introduces a multi-agent orchestration system (`zw_mcp/zw_agent_hub.py`), enabling multiple ZW-speaking agents, each with unique configurations, to collaborate sequentially.

### Core Components:

-   **`zw_mcp/zw_agent_hub.py` (Orchestrator):** Manages multi-agent sessions based on `zw_mcp/agent_profiles.json`.
-   **`zw_mcp/agent_profiles.json` (Agent Definitions):** Lists agents and their individual config file paths (e.g., in `zw_mcp/agents/`).
-   **`zw_mcp/agents/` (Directory for Individual Agent Configs):** Holds JSON configuration files for each agent, allowing unique settings (style, memory, prompt paths, etc.).
    -   The `zw_mcp/handlers/` directory contains the `template_engine.py` module.
-   **`zw_mcp/prompts/`**: Contains seed prompts for agents and the `master_seed.zw` for the hub.
-   **`zw_mcp/agent_runtime/`**: (Created dynamically) For per-agent logs & memory.

### How to Run the Multi-Agent Hub:

1.  Ensure the ZW MCP Daemon (`zw_mcp_daemon.py`) is running.
2.  Prepare agent configurations in `zw_mcp/agent_profiles.json` and `zw_mcp/agents/`, and seed prompts in `zw_mcp/prompts/`.
3.  Run the hub: `python3 zw_mcp/zw_agent_hub.py`.

This framework allows for complex, collaborative dialogues between different AI personas.

---
## ZW Protocol for Blender: Scene Definition & Control (Details)

This section details the ZW blocks used to define and control 3D scenes within Blender, processed by `zw_mcp/blender_adapter.py`.

### Phase 6: Blender Adapter Core Functionality (Initial Object Creation)

This phase bridges the ZW protocol with 3D content creation by introducing an adapter script that runs within Blender. It allows ZW-formatted instructions to be translated into Blender Python (`bpy`) commands, effectively enabling ZW agents or scripts to "speak objects into existence."

### Core Component: `zw_mcp/blender_adapter.py` (and `zw_mcp/zw_mesh.py`)

-   **Purpose:** `blender_adapter.py` is executed by Blender's Python interpreter. It reads a ZW file, parses it using `zw_mcp.zw_parser`, and processes the structure to create 3D content.
-   **Functionality:** Handles `ZW-OBJECT` definitions (including `TYPE`, `NAME`, `LOCATION`, `SCALE`, `CHILDREN` for hierarchies, `MATERIAL`, `COLOR`, `SHADING`, `BSDF` for appearance, and `COLLECTION` for organization).
-   The `blender_adapter.py` script calls functions from `zw_mcp/zw_mesh.py` for detailed mesh creation and material application, especially for `ZW-MESH` blocks.

### Phase 6.6: Procedural Logic Nodes with `ZW-FUNCTION`

The `ZW-FUNCTION` block drives procedural modeling in Blender using Geometry Nodes.
-   **Syntax:** `ZW-FUNCTION: { NAME, TARGET, OPERATION, PARAMS: { ... } }`
-   **Supported Operations:**
    -   `ARRAY`: Creates instances of the `TARGET` object. Params: `COUNT`, `OFFSET`, `MODE`.
    -   `DISPLACE_NOISE`: Modifies `TARGET` geometry with procedural noise. Params: `SCALE`, `STRENGTH`, `AXIS`, `SEED`.

### Phase 6.7: Interactive Drivers with `ZW-DRIVER`

The `ZW-DRIVER` block creates dynamic relationships between object properties.
-   **Syntax:** `ZW-DRIVER: { NAME, SOURCE_OBJECT, SOURCE_PROPERTY, TARGET_OBJECT, TARGET_PROPERTY, EXPRESSION }`
-   Allows one property (e.g., `ControlCube.location.x`) to control another (e.g., `DrivenSphere.scale[2]`) via an expression.

### Phase 6.8: Keyframe Animations with `ZW-ANIMATION`

The `ZW-ANIMATION` block defines keyframed animations for object properties.
-   **Syntax:** `ZW-ANIMATION: { NAME, TARGET_OBJECT, PROPERTY_PATH, INDEX, UNIT, INTERPOLATION, KEYFRAMES: [{FRAME, VALUE}, ...] }`
-   Controls properties like location, rotation, scale over time.

### Phase 6.9: Cameras and Lights with `ZW-CAMERA` and `ZW-LIGHT`

These blocks define camera and light objects.
-   **`ZW-CAMERA`**: `NAME`, `LOCATION`, `ROTATION`, `FOV`, `CLIP_START`, `CLIP_END`, `TRACK_TARGET`, `COLLECTION`.
-   **`ZW-LIGHT`**: `NAME`, `LOCATION`, `ROTATION`, `TYPE` (POINT, SUN, SPOT, AREA), `COLOR`, `ENERGY`, `SHADOW`, `SIZE`, `COLLECTION`.

### Phase 6.10: Procedural Meshes with `ZW-MESH` (UVs, Textures, Export)

The `ZW-MESH:` block defines 3D meshes procedurally.
-   **Syntax:** `ZW-MESH: { NAME, TYPE, PARAMS, DEFORMATIONS: [{TYPE, ...}], MATERIAL: {NAME, BASE_COLOR, EMISSION, EMISSION_COLOR, TEXTURE: {TYPE, FILE, MAPPING, SCALE, ...}}, LOCATION, ROTATION, SCALE, COLLECTION, EXPORT: {FORMAT, FILE} }`
-   Processed by `zw_mcp/zw_mesh.py` (called by `blender_adapter.py`).
-   Supports base primitives, deformations, materials with textures (including UV unwrapping for image textures), and GLB export.

### Phase 6.5: ZW Roundtrip (Blender to ZW Export)

`zw_mcp/blender_exporter.py` exports Blender scene data back into ZW format.
-   Exports selected or all mesh objects.
-   Extracts properties like `TYPE`, `NAME`, `LOCATION`, `SCALE`, `ROTATION`, `MATERIAL`, `COLOR`, `PARENT`, `COLLECTION`.
-   Outputs a flat list of `ZW-OBJECT:` blocks.
-   Usage: `blender --background --python zw_mcp/blender_exporter.py -- --output path/to/export.zw [--all]`

### How to Use the Blender Adapter:

1.  **Prepare ZW Input:** Create a `.zw` file with scene instructions (e.g., `zw_mcp/prompts/blender_scene.zw`).
2.  **Run from Command Line (Headless):**
    ```bash
    blender --background --python zw_mcp/blender_adapter.py -- --input path/to/your_scene.zw
    ```
    (The `--input` argument allows passing a specific ZW file, replacing the old hardcoded path).
3.  **Run from Blender's Scripting Tab (Interactive):** Load and run `zw_mcp/blender_adapter.py`.

This adapter represents a significant step towards using ZW as a descriptive language for generating and manipulating 3D content.

---
## Phase 8.0: Scene Composition & Timeline Control via `ZW-STAGE`

This phase introduces the `ZW-STAGE` block, enabling timeline-based orchestration of scene elements and events within Blender. It allows for sequencing camera switches, object visibility changes, and light animations, forming the foundation for more complex cinematic and narrative control directly from ZW.

-   **Syntax:** `ZW-STAGE: { NAME, TRACKS: [{TYPE, TARGET, START, END, ...params...}] }`
-   **Supported Track Types:**
    -   `CAMERA`: Sets active scene camera.
    -   `VISIBILITY`: Shows/hides objects. Params: `STATE` ("SHOW"|"HIDE").
    -   `LIGHT_INTENSITY`: Animates light energy. Params: `VALUE`, `END_VALUE`.
    -   `PROPERTY_ANIM`: Generic property animation. Params: `PROPERTY_PATH`, `KEYFRAMES`, `INTERPOLATION`, etc.
    -   `MATERIAL_OVERRIDE`: Temporarily changes an object's material. Params: `MATERIAL_NAME`, `START_FRAME`, `END_FRAME`, `RESTORE_ON_END`.
    -   `SHADER_SWITCH`: Changes a shader node input value. Params: `TARGET_NODE`, `INPUT_NAME`, `NEW_VALUE`, `FRAME`.

---
## ZW Tools: Utility & R&D Lab Scripts

This section covers utility scripts that support the development, testing, and management of ZW files and the ZW MCP ecosystem.

### `tools/zw_import_watcher.py`

-   **Purpose:** Monitors a folder (`zw_drop_folder/experimental_patterns/`) for new `.zw` files, performs basic validation, and sorts them into `validated_patterns/` or logs rejections to `research_notes/what_worked.md`.
-   **How to Run:** `python tools/zw_import_watcher.py` from the project root.

---
## ZW Orchestration: `engain_orbit.py`

A new top-level script `engain_orbit.py` is introduced to process `.zwx` files. These files contain a `ZW-INTENT` block and a `ZW-PAYLOAD` block (separated by `---`).

- **Purpose**: `engain_orbit.py` parses the `.zwx` file. Based on the `TARGET_SYSTEM` in `ZW-INTENT` (e.g., "blender" or "ollama"), it routes the `ZW-PAYLOAD` or a derivative to the appropriate processor.
- **Blender Integration**: If `TARGET_SYSTEM` is "blender", `engain_orbit.py` writes the `ZW-PAYLOAD` to a temporary `.zw` file and then invokes Blender in background mode, instructing it to run `zw_mcp/blender_adapter.py` with the path to this temporary file.
- **`blender_adapter.py` Update**: The adapter can now accept an `--input <filepath>` argument to process a specific ZW file passed by an orchestrator like `engain_orbit.py`. It also now includes logic to ignore `ZW-INTENT` blocks if they are encountered in the ZW structure it's parsing (as these are handled by the orchestrator).

### Usage:
```bash
python engain_orbit.py path/to/your_file.zwx [--blender-path /path/to/blender_executable]
```

This allows for a more flexible and intent-driven approach to processing ZW content.

---
## Advanced Scene Assembly (Phase 9.0 & 9.1) - Detailed ZW Blocks & Tools

These phases introduce sophisticated capabilities for modular scene construction using templates and metadata-driven component selection.

### `ZW-COMPOSE`: Assembling Scenes

The `ZW-COMPOSE` block is a powerful directive for assembling complex objects or scenes from pre-defined ZW components.
-   **Syntax:** `ZW-COMPOSE: { NAME, LOCATION, ROTATION, SCALE, COLLECTION, BASE_MODEL, ATTACHMENTS: [{OBJECT, LOCATION, ROTATION, SCALE, MATERIAL_OVERRIDE}], EXPORT }`
-   **Functionality:** Creates a parent Empty. Duplicates and transforms `BASE_MODEL` and `OBJECT`s from `ATTACHMENTS` list, parenting them to the Empty. Allows `MATERIAL_OVERRIDE` for attachments. Can `EXPORT` the assembly to GLB.

This `ZW-COMPOSE` feature allows for building complex, hierarchical models from smaller, reusable ZW components, and is a key enabler for more sophisticated AI-driven design and scene generation.

### `ZW-COMPOSE-TEMPLATE`: Defining Reusable Blueprints
-   **Purpose:** Defines an assembly blueprint with abstract "slots" that need to be filled by ZW components matching certain criteria.
-   **Syntax:** `ZW-COMPOSE-TEMPLATE: { NAME, SLOTS: [{ID, ROLE, REQUIRED_TAGS, OPTIONAL_TAGS, COUNT, LOCAL_TRANSFORM, MATERIAL_OVERRIDE_GROUP}] }`

### `ZW-METADATA`: Tagging Components for Discovery
-   **Purpose:** Attaches semantic tags and other metadata to ZW components (usually inline within `ZW-MESH` or `ZW-OBJECT` blocks).
-   **Syntax (Inline):** `METADATA: { TAGS: [...], SUITABILITY: [...], DESCRIPTION: "..." }`

### Core Engine: `zw_mcp/handlers/template_engine.py`
-   **`ZWMetadataRegistry` Class:** Manages a catalog of ZW components and their metadata, indexed by tags.
-   **`ZWTemplateEngine` Class:** Parses templates, selects components from the registry for slots (based on tags and strategy), and generates concrete `ZW-COMPOSE` blocks.
-   **Utility Functions:** `load_mesh_registry_from_files()`.

### CLI Tool: `zw_mcp/smart_assembler.py`

To facilitate the use of the `ZWTemplateEngine` and `ZWMetadataRegistry`, the `smart_assembler.py` CLI tool is provided.

#### Purpose:

The `smart_assembler.py` script orchestrates:
1.  Loading ZW parts (with `METADATA`) from a parts directory (e.g., `zw_mcp/mesh/`).
2.  Building a `ZWMetadataRegistry`.
3.  Loading a `ZW-COMPOSE-TEMPLATE` from a `.zw` file (e.g., from `zw_mcp/templates/`).
4.  Using `ZWTemplateEngine` to fill the template slots with matching parts.
5.  Outputting the generated `ZW-COMPOSE` block (as ZW text), ready for `blender_adapter.py`.

#### Key Command-Line Arguments:

-   `--template <path>` or `-t <path>`: **(Required)** Path to the `ZW-COMPOSE-TEMPLATE` file.
-   `--mesh-dir <directory_path>` or `-m <directory_path>`: Path to ZW part definitions (default: `zw_mcp/mesh`).
-   `--output <filepath>` or `-o <filepath>`: Optional. Path to save the generated `ZW-COMPOSE` ZW string. (stdout if omitted).
-   `--strategy <random|first|best_fit>` or `-s <random|first|best_fit>`: Selection strategy (default: `best_fit`).
-   `--save-index <filepath>`: Optional. Saves the metadata registry index to a JSON file.
-   `--list-tags`: Optional. Lists all unique tags from the mesh directory and exits.
-   `--verbose` or `-v`: Optional. Enables more detailed console output.

This system moves towards a more generative and AI-friendly approach, where ZW defines not just explicit scenes but also the rules, components, and templates for creating a multitude of scene variations.
>>>>>>> ollama-mcp-phase2-daemon
