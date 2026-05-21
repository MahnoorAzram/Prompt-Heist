import os
import datetime
import requests
from dotenv import load_dotenv
import json
# Load environment variables from .env
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

# Retrieve API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

def get_narrative_director_prompt():
    directive_path = os.path.join(os.path.dirname(__file__), '..', 'directives', 'narrative_director.md')
    with open(directive_path, 'r', encoding='utf-8') as f:
        return f.read().strip()

def generate_mission(mission_number, player_archetype, previous_mission_summary):
    """Generate a mission description using the narrative_director directive via Gemini API."""
    system_prompt = get_narrative_director_prompt()
    user_prompt = f"""
Inputs:
- mission_number: {mission_number}
- player_archetype: {player_archetype}
- previous_mission_summary: {previous_mission_summary}
"""
    # Try multiple Gemini models
    models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.5-flash", "gemini-2.0-flash"]
    last_error = None
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }
        try:
            response = requests.post(url, json=payload, timeout=30)
            # Log raw response for debugging
            traces_dir = os.path.join(os.path.dirname(__file__), '..', 'traces')
            os.makedirs(traces_dir, exist_ok=True)
            timestamp = datetime.datetime.utcnow().isoformat().replace(':', '-')
            log_path = os.path.join(traces_dir, f"generate_mission_raw_{model}_{timestamp}.json")
            with open(log_path, 'w', encoding='utf-8') as log_f:
                log_f.write(response.text)
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text']
                return json.loads(text.strip())
            else:
                last_error = f"Model {model} returned {response.status_code}: {response.text}"
        except Exception as e:
            last_error = f"Model {model} exception: {e}"
    placeholder = {
        "mission_codename": f"Placeholder Mission {mission_number}",
        "target": "Generic target",
        "location_flavor": "Standard facility",
        "antagonist_name": "Placeholder Antagonist",
        "stakes": "Standard stakes",
        "story_arc_note": "Fallback mission",
        "briefing_text": "This is a fallback mission generated due to API failure.",
        "mission_hook": "No special hook"
    }
    return placeholder

if __name__ == "__main__":
    # Test execution
    try:
        res = generate_mission(
            mission_number=3,
            player_archetype="The Ghost",
            previous_mission_summary="Infiltrated the museum without setting off any alarms and extracted via the roof."
        )
        print(json.dumps(res, indent=2))
    except Exception as e:
        print(f"Error during mission generation: {e}")
