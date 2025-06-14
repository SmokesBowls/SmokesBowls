Markdown

---
> 🚦 **Phase 9.2.1 — Intent Routing Operational**
> This version establishes the `.zwx` intent-driven architecture with `engain_orbit.py` as the central router,
> including schema validation, execution logging, and foundational multi-engine support.
---

# ZW MCP Ecosystem: AI-Powered Creative Orchestration

![ZW MCP System Diagram](https://via.placeholder.com/800x400?text=ZW+MCP+System+Architecture)
*A unified framework for AI-assisted content creation, 3D modeling, and narrative generation*

## Overview

ZW MCP is an advanced ecosystem that bridges AI-powered language models with creative tools through the ZW protocol - a structured format for describing scenes, animations, and narratives. This system features:

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

Key Features
Core Components
Component	Purpose	Key Technologies
ZW MCP Daemon	Networked API endpoint	Python, TCP Socket
Ollama Handler	AI communication layer	REST API, JSON
ZW Parser	Protocol validation/translation	Python, Regex
Autonomous Agents	AI-powered task execution	State machines, Memory
Blender Adapter	3D content generation	bpy, Geometry Nodes
EngAIn-Orbit Router	Processes .zwx files, routes ZW-PAYLOAD based on intent	Python, .zwx
ZW-INTENT Validator	Validates ZW-INTENT blocks in .zwx files	Python (tools/intent_utils.py)
Advanced Capabilities

    Multi-Agent Orchestration
    Mermaid

    graph LR
      A[Master Seed] --> B[Agent 1]
      B --> C[Agent 2]
      C --> D[Agent 3]
      D --> E[Final Output]

    Procedural 3D Generation
        Object hierarchies with parenting
        Material/shader configuration
        Geometry node operations
        Keyframe animation system

    Networked Services
        TCP daemon (port 7421)
        Client/server architecture
        Session logging/monitoring

Getting Started
Prerequisites

    Python 3.9+
    Ollama (local instance)
    Blender 3.0+
    Required packages: pip install requests numpy

Installation
bash

git clone https://github.com/SmokesBowls/zw_mcp.git
cd zw_mcp
conda create -n zw_env python=3.10
conda activate zw_env
pip install -r requirements.txt

Basic Usage

    Start the TCP daemon:
    bash

python zw_mcp/zw_mcp_daemon.py

Send a ZW prompt:
bash

python zw_mcp/client_example.py prompts/example.zw

Generate 3D content in Blender:
bash

    blender --background --python zw_mcp/blender_adapter.py

    (See tools/engain_orbit.py for the new primary way to execute ZW content via .zwx files)

System Architecture
Core Components
Code

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
    ├── orbit_watchdog.py # Automated ZWX file processor
    ├── intent_utils.py   # ZW-INTENT validator
    ├── exporter.py       # Blender→ZW conversion
    └── watcher.py        # Directory monitoring

Workflow Diagram
Mermaid

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

Advanced Features
Multi-Agent Collaboration

Configure agent teams in agents/profiles.json:
JSON

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

Blender Integration Examples

Create a material:
zw

ZW-MATERIAL:
  NAME: Emerald
  COLOR: "#50C878"
  ROUGHNESS: 0.2
  METALLIC: 0.8

Animate an object:
zw

ZW-ANIMATION:
  TARGET: "Orb"
  PROPERTY: rotation
  KEYFRAMES:
    - FRAME: 0
      VALUE: (0, 0, 0)
    - FRAME: 100
      VALUE: (0, 0, 360)

Tools and Utilities
tools/engain_orbit.py: ZWX Execution Router

The engain_orbit.py script (located in the tools/ directory) is the primary entry point for executing .zwx files.

Key aspects:

    .zwx File Format: Combines a ZW-INTENT block (metadata for routing and execution) with a ZW-PAYLOAD block (the ZW commands).
    YAML

    ZW-INTENT:
      TARGET_SYSTEM: blender
      TARGET_FUNCTION: create_scene
      DESCRIPTION: A simple cube
    ---
    ZW-PAYLOAD:
      OBJECT: MyCube
        TYPE: Cube
        SIZE: 2

    Schema Validation: The ZW-INTENT block is automatically validated by tools/intent_utils.py to ensure required fields like TARGET_SYSTEM are present.
    Execution Logging: All routing attempts, successes, and failures are logged with timestamps to zw_mcp/logs/orbit_exec.log.

tools/orbit_watchdog.py: Automated ZWX File Processor

    Monitors a specified directory for new .zwx files and uses engain_orbit.py to validate and route them.
    Moves processed files to executed/ or failed/ subfolders, and logs activities to zw_mcp/logs/orbit_watchdog.log.

Usage:
bash

python3 tools/orbit_watchdog.py

or for a single scan:
bash

python3 tools/orbit_watchdog.py --once

Development Roadmap
Current Features

    ZW protocol parser/validator
    TCP networking layer
    Ollama API integration
    Blender scene generation
    Multi-agent orchestration
    EngAIn-Orbit .zwx router (tools/engain_orbit.py)
    ZW-INTENT schema validation (tools/intent_utils.py)
    Execution logging for EngAIn-Orbit (zw_mcp/logs/orbit_exec.log)
    Automated ZWX file processing (tools/orbit_watchdog.py)

Planned Features

    Godot engine integration (Stubbed in engain_orbit.py)
    Web-based control interface
    Versioned memory system
    Physics simulation support
    Audio-reactive animations

Testing and Validation

A test suite verifies the ZWX intent-routing pipeline.

Automated Test Suite:
Run all tests with:
bash

python3 tools/test_orbit_routing.py

Test logs: zw_mcp/logs/orbit_test_results.log

Manual Testing:
Run orbit_watchdog.py and place .zwx files in zw_drop_folder/validated_patterns/.
Contributing

We welcome contributions! Please follow these steps:

    Fork the repository
    Create your feature branch (git checkout -b feature/amazing-feature)
    Commit your changes (git commit -m 'Add amazing feature')
    Push to the branch (git push origin feature/amazing-feature)
    Open a pull request

License

Distributed under the MIT License. See LICENSE for more information.
Contact

SmokesBowls - @YourTwitter - email@example.com
Project Link: https://github.com/SmokesBowls/zw_mcp
Python

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

Ready to create? Start with our Quickstart Guide or explore the Example Gallery. Use tools/engain_orbit.py to run .zwx examples.
