# Recall — The AI Brain for Developers

> Stop Googling commands. Recall remembers everything.

Recall is an AI-powered terminal tool that understands natural language, remembers your history, fixes your errors, and automates your workflows — all inside your terminal.

## Install

```bash
pip install recall-ai
```

## Setup

```bash
recall --setup
```

## Usage

```bash
# Natural language to command
recall "how to check running ports"

# See your history
recall --history

# Fix an error
recall --error "ModuleNotFoundError: No module named pandas"

# Save a workflow
recall --save "deploy"

# Run a workflow
recall --run "deploy"

# List all workflows
recall --list-workflows
```

## Features

- Natural language → exact terminal command
- Persistent memory — remembers your history
- Context aware — learns from past queries
- Error intelligence — detects and fixes errors automatically
- Workflow automation — save and run command sequences
- Cross platform — Windows, Mac, Linux

## Built With

Python · FastAPI · AWS EC2 · Anthropic Claude API

---

Built by [Muhammad Bilal Ur Rehman](https://github.com/mbilalrehman)
