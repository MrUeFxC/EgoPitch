# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EgoPitch is a World Cup Star AI Interview Simulator - an AI agent system that simulates deep interviews with football stars (like Cristiano Ronaldo, Messi, Mbappé). The system uses a **three-layer personality model** where AI personas evolve from "public persona" to "deep ego" to "explosive mode" based on interview triggers.

## Architecture

The system is designed around these core concepts:

1. **Personality Layers** - Stars have three states that activate progressively:
   - Layer 1 (Public): Professional, avoids controversy
   - Layer 2 (Ego): Shows strong self-esteem, references personal honors, tone stiffens
   - Layer 3 (Nuke): Explosive mode - reveals locker room secrets, names critics

2. **Anger Value System** - `Current_Anger = (Trigger_Words × 10) + (Negative_Social_Sentiment × 5)`

3. **Key Components** (planned):
   - **Instigator Agent**: Probes "pain points", deepens topics that trigger anger spikes
   - **Social Media Pulse**: Injects simulated X/TikTok comments as external stimuli
   - **Multi-modal Output**: Text stream + ElevenLabs voice cloning + visual generation

## Tech Stack (Planned)

- **Backend**: Python 3.12+, LangGraph for state management
- **LLM**: Claude or GPT-4 (strong role-play capability)
- **Configuration**: State-driven JSON for personality fragments (no vector DB)
- **Frontend**: Next.js for real-time chat/streaming UI
- **Voice**: ElevenLabs API

## Commands

```bash
# Run the application
python main.py

# Install dependencies (uses uv or pip)
uv sync
# or
pip install -e .
```

## Development Notes

- The project is in early prototype stage - architecture decisions should align with the vision in README.md
- Personality configs should be lightweight JSON files, not heavy vector databases
- Focus on "simple logic, explosive effects" - the AI should understand star temperaments, not football tactics