# Prompt Heist — Bella Ciao
## Hackathon Challenge 4 — Agentic Game Quest

## One Line Pitch
Every game tests your reflexes. Prompt Heist tests how well you think.

## What Is This Game
You are The Professor. Your crew of four specialists is inside the 
Central Reserve Bank of Verano City:
- KHATTAK SAHAB — controls hostages, ground floor
- KARDAR — physical security, stairwells
- PINKY — vault specialist
- KHOKAAR — tech expert, cameras

Your only weapon is your words. You write text prompts to guide your crew.
Six AI agents read every word and execute your plan based on quality.
Vague plan → crew fails → police captures a member.
Detailed precise plan → crew succeeds → vault opens.

## Technical Architecture
Flutter App (Mobile)
        ↓ HTTP POST
Flask Server (api_server.py) — Port 5000
        ↓ Python call
Master Orchestrator (master_orchestrator.py)
        ↓ Coordinates
    ┌───┴────────────────────────┐
    ↓                            ↓
Prompt Evaluator          Crisis Generator
(score_prompt.py)         (generate_crisis.py)
    ↓                            ↓
Police Counter            Mission Director
(police_counter.py)       (generate_mission.py)
    ↓                            ↓
        Performance Profiler
        (profile_player.py)
    ↓
Gemini API (All agents use this)

## The 6 AI Agents

### Agent 1 — Prompt Evaluator (score_prompt.py)
Reads every player prompt and scores it 0-100 on four dimensions:
- Clarity: does crew know exactly what to do?
- Specificity: are names, locations, timing defined?
- Feasibility: is this actually possible?
- Creativity: is it tactically clever?

### Agent 2 — Master Orchestrator (master_orchestrator.py)
Brain of the entire game. Coordinates all other agents.
Decides whether to trigger crisis, police move, or difficulty adjustment.

### Agent 3 — Crisis Generator (generate_crisis.py)
Every 3 rounds generates a completely new unexpected emergency.
Validates: is this solvable? Is it different from last crisis? Is it fair?

### Agent 4 — Police Counter Agent (police_counter.py)
Studies player last 3 moves every 2 rounds.
Detects patterns. Adapts and counters specifically.

### Agent 5 — Mission Director (generate_mission.py)
Generates unique mission briefing at start of each new game.
No two games start the same way.

### Agent 6 — Performance Profiler (profile_player.py)
Watches entire session. Analyzes all prompts and scores at end.
Feeds into difficulty adjustment for next mission.

## Agentic Behavior Loop
Every round this loop runs automatically:

OBSERVE:  reads last 3 player prompts
INFER:    detects dominant pattern and strategy
DECIDE:   selects counter-tactic
ACT:      deploys police response
EVALUATE: tracks if player adapts

## File Structure
phantom-vault/
├── execution/
│   ├── api_server.py          ← Flask server, port 5000
│   ├── master_orchestrator.py ← Game brain, coordinates all agents
│   ├── score_prompt.py        ← Prompt evaluator agent
│   ├── generate_crisis.py     ← Crisis generator agent
│   ├── police_counter.py      ← Police counter agent
│   ├── generate_mission.py    ← Mission director agent
│   ├── profile_player.py      ← Performance profiler agent
│   └── simulate_phase.py      ← Heist simulation
├── directives/
│   ├── master_orchestrator.md
│   ├── prompt_evaluator.md
│   ├── crisis_generator.md
│   ├── police_counter_agent.md
│   ├── narrative_director.md
│   └── performance_profiler.md
├── traces/
│   ├── trace_mission.json
│   ├── trace_game_round1.json
│   ├── trace_game_round2.json
│   ├── trace_game_round3.json
│   ├── trace_crisis.json
│   ├── trace_police.json
│   ├── trace_profiler.json
│   └── README_traces.txt
└── README.md

## API Endpoints

### POST /start_mission
Returns AI-generated mission briefing.
Input: {"mission_number": 1, "player_archetype": "Planner", "previous_summary": null}

### POST /game
Main game loop. Call every time player submits a prompt.
Input: {"player_prompt": "string", "prompt_count": 1, "vault_progress": 0, 
        "police_alert": 0, "team_status": {...}, "all_scores": [], "mission_number": 1}

### POST /end_mission
Performance analysis after mission ends.
Input: {"all_scores": [72, 45, 88], "all_prompts": ["prompt1", "prompt2"]}

## How To Run

### Backend
pip install flask flask-cors google-generativeai python-dotenv requests
Add GEMINI_API_KEY to .env file
cd execution
python api_server.py

### Flutter
cd bella_ciao
flutter run

## Baseline Comparison
| Feature | Fixed Rules | Agentic System |
|---|---|---|
| Difficulty | if score > 5: difficulty++ | 5 live signals calibrated per mission |
| Police | Fixed patrol patterns | Observes player pattern, targeted counter |
| Crisis | Random fixed pool | Context-aware, never repeats |
| Prompt eval | Keyword matching | Semantic scoring across 4 dimensions |
| Missions | Pre-built levels | Infinite procedural generation |

## Privacy
No personal data stored. All names fictional. 
Player prompts processed only within Gemini API.

## Team
Built for Hackathon Challenge 4 — Agentic Game Quest