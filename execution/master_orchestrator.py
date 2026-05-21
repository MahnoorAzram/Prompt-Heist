import os
import json
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

# Import execution scripts (same directory)
from score_prompt import score_prompt
from police_interrogation import run_police_interrogation
from simulate_phase import simulate_phase
from twist_agent import run_twist_agent
from generate_crisis import generate_crisis
from police_counter import police_counter

# Load environment variables from .env (project root)
dotenv_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path)


def run_orchestrator(player_prompt: str, game_state: dict) -> dict:
    """Run the full Master Orchestrator flow.

    The function calls the four agents in order, merges their outputs, and
    returns a single JSON‑serialisable dictionary matching the required schema.

    Expected keys in ``game_state``:
        - ``vault_progress`` (int 0‑100)
        - ``police_alert``   (int 1‑5)
        - ``prompt_count``   (int)
        - other fields are retained for possible future use.
    """
    # ---------------------------------------------------------------------
    # 1️⃣ Agent 1 – Score the player prompt
    # ---------------------------------------------------------------------
    try:
        score_result = score_prompt(player_prompt)
    except Exception as e:
        return {"error": f"Score prompt failed: {e}"}

    # ---------------------------------------------------------------------
    # 1.5️⃣ Agent – Police Interrogation (gate check on prompt quality)
    # ---------------------------------------------------------------------
    interrogation_result = run_police_interrogation(score_result.get("total", 0))

    # ---------------------------------------------------------------------
    # 2️⃣ Agent 2 – Simulate the crew action based on the total score
    # ---------------------------------------------------------------------
    try:
        simulate_result = simulate_phase(
            prompt_score=score_result.get("total", 0),
            vault_progress=game_state.get("vault_progress", 0),
            police_alert=game_state.get("police_alert", 0),
        )
    except Exception as e:
        return {"error": f"Simulate phase failed: {e}"}

    # ---------------------------------------------------------------------
    # 2.5️⃣ Agent – Twist Agent (dynamic rule change for next mission)
    # ---------------------------------------------------------------------
    twist_result = run_twist_agent(score_result.get("total", 0), simulate_result)

    # ---------------------------------------------------------------------
    # 3️⃣ Conditional Agent 3 – Crisis generation (every 3 prompts)
    # ---------------------------------------------------------------------
    should_generate_crisis = (game_state.get("prompt_count", 0) % 3 == 0)
    crisis_data = None
    if should_generate_crisis:
        try:
            crisis_data = generate_crisis(player_prompt)
        except Exception as e:
            # Preserve flow – surface the error inside the payload
            crisis_data = {"error": f"Crisis generation failed: {e}"}

    # ---------------------------------------------------------------------
    # 4️⃣ Conditional Agent 4 – Police counter move (every 2 prompts)
    # ---------------------------------------------------------------------
    should_generate_police_move = (game_state.get("prompt_count", 0) % 2 == 0)
    police_move_data = None
    if should_generate_police_move:
        try:
            police_move_data = police_counter()
        except Exception as e:
            police_move_data = {"error": f"Police counter failed: {e}"}

    # ---------------------------------------------------------------------
    # 5️⃣ Combine all results into the final response schema
    # ---------------------------------------------------------------------
    final_response = {
        "total": score_result.get("total"),
        "grade": score_result.get("grade"),
        "clarity": score_result.get("clarity"),
        "specificity": score_result.get("specificity"),
        "feasibility": score_result.get("feasibility"),
        "creativity": score_result.get("creativity"),
        "feedback": score_result.get("feedback"),
        "team_action": score_result.get("team_action"),
        "situation_update": simulate_result.get("situation_update"),
        "vault_delta": simulate_result.get("vault_delta"),
        "police_alert_delta": simulate_result.get("police_alert_delta"),
        "team_caught": score_result.get("team_caught") or simulate_result.get("team_caught"),
        "should_generate_crisis": should_generate_crisis,
        "crisis": crisis_data if should_generate_crisis else None,
        "should_generate_police_move": should_generate_police_move,
        "police_move": police_move_data if should_generate_police_move else None,
        "police_interrogation": interrogation_result,
        "twist": twist_result,
    }

    return final_response


if __name__ == "__main__":
    # Example invocation for quick manual testing
    test_player_prompt = "tokyo secure the perimeter while berlin starts drilling the vault."
    test_game_state = {
        "prompt_count": 3,
        "vault_progress": 45,
        "police_alert": 2,
        "team_status": ["berlin", "tokyo", "nairobi", "rio"],
        "all_scores": [75, 80],
        "mission_number": 1,
    }
    print(json.dumps(run_orchestrator(test_player_prompt, test_game_state), indent=2))
