# Implementation Walkthrough — Prompt Heist

## Day 1 — Agent Architecture

### Step 1: Designed 6-agent system
Decided on separation of concerns:
- One agent per responsibility
- Master orchestrator coordinates all
- Each agent has its own directive markdown file

### Step 2: Created directive files
Built system prompts for each agent in directives/ folder.
Each directive defines: role, inputs, outputs, rules, edge cases.

### Step 3: Implemented Python execution scripts
Built deterministic Python scripts for each agent.
Each script reads its directive and calls Gemini API.

### Step 4: Built Master Orchestrator
Wired all agents together in sequence:
1. score_prompt → evaluate player prompt
2. generate_crisis → if prompt_count % 3 == 0
3. police_counter → if prompt_count % 2 == 0
4. profile_player → on mission end

### Step 5: Built Flask API server
Created api_server.py with 3 endpoints:
- POST /start_mission
- POST /game  
- POST /end_mission

## Day 2 — Frontend Integration

### Step 6: Flutter app structure
Built 6 screens:
- Splash screen
- Main menu
- Mission briefing
- Game screen (main)
- Win screen
- Lose screen

### Step 7: AI Service connection
Connected Flutter to Flask backend via HTTP POST.
URL: http://10.0.2.2:5000/game (emulator)
URL: http://localhost:5000/game (physical device)

### Step 8: Game state management
Flutter tracks:
- vault_progress (0-100)
- police_alert (1-5)
- prompt_count
- team_status for each member
- all_scores for performance profiler

### Step 9: Crisis and Police overlays
Built real-time overlays:
- Crisis screen with countdown timer
- Police move card sliding from bottom
- Caught overlay when team member captured

### Step 10: Agent trace display
Built live agent log panel showing:
- Which agent fired
- What decision was made
- Score and timestamp

## Key Technical Decisions

### Why Flask over FastAPI
Simple, lightweight, fast to build.
CORS handled with flask-cors.

### Why Gemini API directly
More control over prompts.
Can read directive files as system prompts.

### Why separate agents instead of one prompt
Separation of concerns.
Each agent specialized = better outputs.
Easier to debug when something goes wrong.

## Challenges Solved

### Challenge 1: Gemini returning text instead of JSON
Added JSON extraction logic to strip markdown wrappers.
Added fallback for malformed responses.

### Challenge 2: Quota limits
Added exponential backoff retry logic (3 attempts).
Added fallback responses when quota exceeded.

### Challenge 3: Flutter-Backend mismatch
Fixed request format to match backend expectations.
Added proper error handling for timeouts.

## Agent Trace Evidence
All agent traces saved in traces/ folder.
Each trace shows: observation → inference → decision → action → outcome.
This proves genuine agentic behavior, not hardcoded rules.
