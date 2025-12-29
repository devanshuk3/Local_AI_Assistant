# Local AI Assistant

A **local AI assistant** framework in Python that lets you interact with large language models (LLMs) running locally (no internet required).  
This project provides tools to load, query, and manage local LLMs with support for different execution modes — ideal for building privacy-first chatbot, automation, or AI CLI/GUI tools.

---

## 🧠 Overview

**Local_AI_Assistant** is a Python-based assistant framework that:

- Loads and interacts with **local LLMs**  
- Supports multiple *modes* and execution strategies  
- Includes utilities for running, executing, and managing LLM prompts  
- Is designed to work with local LLM backends (e.g., Ollama, LocalAI, KoboldCPP, etc.)

> Local LLM assistants keep your data on **your machine** and avoid third-party APIs, enabling *offline and private usage* similar to other local AI projects.:contentReference[oaicite:0]{index=0}

---

## 🚀 Features

✔ Support for local LLM execution  
✔ Modular executor architecture  
✔ Multiple prompt handling modes  
✔ Configurable AI settings  
✔ AutoHotkey helper integration (optional)

---

## 📁 Repository Structure
Local_AI_Assistant/
├── ahk/ # AutoHotkey assets
├── ahk_generator.py # Generates AutoHotkey scripts
├── config.py # Configuration & settings
├── confirm_dialog.py # UI prompt helpers
├── executor.py # Core execution logic
├── llm.py # LLM API interface
├── local_llm.py # Local LLM backend handlers
├── main.py # Application entrypoint
├── mode_executor.py # Mode-based execution logic
├── modes.py # Supported assistant modes
└── requirements.txt # Python dependencies


---

## 🛠️ Requirements

Make sure you have:

- **Python 3.8+**
- Dependencies installed:

```bash
pip install -r requirements.txt

python -m pip install -r requirements.txt



**Configure your assistant

Edit config.py to choose your local LLM backend, prompt settings, context limits, and model paths. For example:

# config.py (example)
MODEL_BACKEND = "ollama"
MODEL_NAME = "llama3:8b"**


