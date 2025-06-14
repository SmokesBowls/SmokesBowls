---
> 🚦 **Phase 9.2.1 — Intent Routing Operational**
> This version establishes the `.zwx` intent-driven architecture with `engain_orbit.py` as the central router,
> including schema validation, execution logging, and foundational multi-engine support.
---
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

A key component in this ecosystem is **EngAIn-Orbit (`tools/engain_orbit.py`)**, which processes `.zwx` files.
The `.zwx` format separates `ZW-INTENT` (the semantic directive, e.g., target system and function)
from `ZW-PAYLOAD` (the actual ZW data for the creative task). This allows for clear,
AI-dispatchable instructions and modular routing to different backend engines.

```python
# Example ZW Protocol Snippet
ZW-NARRATIVE:
  TITLE: The Awakening
  CHARACTERS:
    - NAME: Tran
      ROLE: Protagonist
  SCENE:
    - OBJECT: Ancient_Relic
      TYPE: Artifact
      MATERIAL: Obsidian
      ANIMATION: Pulsate
```

## Key Features

### Core Components
| Component | Purpose | Key Technologies |
|-----------|---------|------------------|
| **ZW MCP Daemon** | Networked API endpoint | Python, TCP Socket |
| **Ollama Handler** | AI communication layer | REST API, JSON |
| **ZW Parser** | Protocol validation/translation | Python, Regex |
| **Autonomous Agents** | AI-powered task execution | State machines, Memory |
| **Blender Adapter** | 3D content generation | bpy, Geometry Nodes |
| **EngAIn-Orbit Router** | Processes `.zwx` files, routes ZW-PAYLOAD based on ZW-INTENT | Python, `.zwx` |
| **ZW-INTENT Validator** | Validates `ZW-INTENT` blocks in `.zwx` files for structural integrity | Python (in `tools/intent_utils.py`) |

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

### Intent-Driven Execution with EngAIn-Orbit
The `engain_orbit.py` script (located in the `tools/` directory) is the primary entry point for executing `.zwx` files.
Key aspects of this system include:
- **`.zwx` File Format**: Combines a `ZW-INTENT` block (metadata for routing and execution) with a `ZW-PAYLOAD` block (the ZW commands).
  ```
  ZW-INTENT:
    TARGET_SYSTEM: blender
    TARGET_FUNCTION: create_scene
    DESCRIPTION: A simple cube
  ---
  ZW-PAYLOAD:
    OBJECT: MyCube
      TYPE: Cube
      SIZE: 2
  ```
- **Schema Validation**: The `ZW-INTENT` block is automatically validated by `tools/intent_utils.py` to ensure required fields like `TARGET_SYSTEM` are present, aiding in early error detection and debugging of `.zwx` files.
- **Execution Logging**: All routing attempts, successes, and failures (including validation errors) by `engain_orbit.py` are logged with timestamps to `zw_mcp/logs/orbit_exec.log`. This provides a detailed audit trail for diagnostics. Example:
  ```log
  [2023-10-27 10:00:00] ✔ Routed: examples/my_scene.zwx → blender
  [2023-10-27 10:00:05] ❌ Validation FAILED: examples/bad_scene.zwx - Missing TARGET_SYSTEM in ZW-INTENT block.
  ```

## Getting Started

### Prerequisites
- Python 3.9+
- [Ollama](https://ollama.ai/) (local instance)
- Blender 3.0+
- Required packages: `pip install requests numpy`

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

3. Generate 3D content in Blender:
```bash
blender --background --python zw_mcp/blender_adapter.py
```
(See `tools/engain_orbit.py` for the new primary way to execute ZW content via `.zwx` files)


## System Architecture

### Core Components
```
zw_mcp/
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
    ├── engain_orbit.py   # ZWX intent router
    ├── intent_utils.py   # ZW-INTENT validator
    ├── exporter.py       # Blender→ZW conversion
    └── watcher.py        # Directory monitoring
```

### Workflow Diagram
```mermaid
sequenceDiagram
    participant User
    participant AgentHub
    participant ZWDaemon
    participant Ollama
    participant Blender

    User->>AgentHub: Initiate workflow
    AgentHub->>ZWDaemon: Send ZW prompt
    ZWDaemon->>Ollama: Request generation
    Ollama->>ZWDaemon: Return ZW response
    ZWDaemon->>Blender: Create 3D scene
    Blender->>AgentHub: Return result
    AgentHub->>User: Final output
```

## Advanced Features

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
- [x] EngAIn-Orbit `.zwx` router (`tools/engain_orbit.py`)
- [x] ZW-INTENT schema validation (`tools/intent_utils.py`)
- [x] Execution logging for EngAIn-Orbit (`zw_mcp/logs/orbit_exec.log`)


### Planned Features
- [ ] Godot engine integration (Stubbed in `engain_orbit.py` for basic routing)
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
Use `tools/engain_orbit.py` to run `.zwx` examples.
