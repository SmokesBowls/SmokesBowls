ZW MCP Ecosystem: AI-Powered Creative Orchestration

ZW MCP System Diagram
A unified framework for AI-assisted content creation, 3D modeling, and narrative generation
Overview

ZW MCP is an advanced ecosystem that bridges AI-powered language models with creative tools through the ZW protocol—a structured format for describing scenes, animations, and narratives. This system features:

    🧠 AI-assisted creation using Ollama language models
    🎨 Procedural 3D content generation in Blender
    🤖 Multi-agent collaboration for complex tasks
    🔄 Roundtrip workflows between text and 3D environments
    ⚡ Real-time networked communication between components

Core Components
Component	Purpose	Key Technologies
ZW MCP Daemon	Networked API endpoint	Python, TCP Socket
Ollama Handler	AI communication layer	REST API, JSON
ZW Parser	Protocol validation/translation	Python, Regex
Autonomous Agents	AI-powered task execution	State machines, Memory
Blender Adapter	3D content generation	bpy, Geometry Nodes
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

    Python 3.9+ (3.10 recommended)
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

Alternative CLI Usage

You can also run the direct server script with advanced command-line arguments:
bash

python3 zw_mcp/zw_mcp_server.py zw_mcp/prompts/example.zw --out zw_mcp/responses/response_001.zw --log zw_mcp/logs/session.log

or
bash

python3 zw_mcp/zw_mcp_server.py zw_mcp/prompts/example.zw

System Architecture & Directory Structure
text

zw_mcp/
├── zw_mcp_daemon.py        # TCP Daemon server for ZW message passing
├── zw_mcp_server.py        # Original CLI tool for direct Ollama interaction
├── client_example.py       # Example TCP client for zw_mcp_daemon.py
├── ollama_handler.py       # Handles API requests to Ollama
├── zw_parser.py            # ZW parsing and formatting utilities
├── test_zw_parser.py       # Unit tests for zw_parser
├── blender_adapter.py      # Script to run within Blender to interpret ZW for scene creation
├── blender_exporter.py     # Script for Blender to export scenes to ZW
├── zw_mesh.py              # Module for procedural mesh generation in Blender
├── handlers/
│   └── template_engine.py  # ZWTemplateEngine and ZWMetadataRegistry
├── smart_assembler.py      # CLI tool for template-based scene assembly
├── agents/
│   ├── narrator_config.json
│   └── historian_config.json
├── agent_runtime/          # (Created dynamically) Per-agent logs & memory
├── prompts/                # ZW seed prompts and examples
├── templates/              # Definitions for ZW-COMPOSE-TEMPLATE
├── mesh/                   # Library of ZW component parts with METADATA
├── responses/              # Default output for some older CLI tools
└── logs/                   # General logging directory

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

Development Roadmap
Current Features

    ZW protocol parser/validator
    TCP networking layer
    Ollama API integration
    Blender scene generation
    Multi-agent orchestration

Planned Features

    Godot engine integration
    Web-based control interface
    Versioned memory system
    Physics simulation support
    Audio-reactive animations

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
