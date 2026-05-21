import os
import json
import requests
from dotenv import load_dotenv


def police_counter():
    # Load environment variables from .env file
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(env_path)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Error: GEMINI_API_KEY not found in .env")

    # Load system prompt from police_counter_agent.md
    directives_path = os.path.join(os.path.dirname(__file__), '..', 'directives', 'police_counter_agent.md')
    if os.path.exists(directives_path):
        with open(directives_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read().strip()
    else:
        raise FileNotFoundError("police_counter_agent.md not found")

    # Player prompt as requested
    player_prompt = """
last_3_prompts:
1. PINKY distract the guard near entrance
2. PINKY create another distraction on floor 1
3. PINKY distract again near east door
score: 35
team: KHATTAK SAHAB active, KARDAR active, PINKY active, KHOKAAR active
Generate police counter move now.
"""

    # Try multiple Gemini models
    models_to_try = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.5-flash",
        "gemini-2.0-flash"
    ]

    last_error = None
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "system_instruction": {"parts": {"text": system_prompt}},
            "contents": [{"parts": [{"text": player_prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            # Log raw response for debugging
            traces_dir = os.path.join(os.path.dirname(__file__), '..', 'traces')
            os.makedirs(traces_dir, exist_ok=True)
            timestamp = datetime.datetime.utcnow().isoformat().replace(':', '-')
            log_path = os.path.join(traces_dir, f"police_counter_raw_{model}_{timestamp}.json")
            with open(log_path, 'w', encoding='utf-8') as log_f:
                log_f.write(response.text)
            if response.status_code == 200:
                result = response.json()
                text_response = result['candidates'][0]['content']['parts'][0]['text']
                json_data = json.loads(text_response.strip())
                return json_data
            else:
                last_error = f"Model {model} returned status {response.status_code}: {response.text}"
        except Exception as e:
            last_error = f"Model {model} failed with exception: {str(e)}"
    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

if __name__ == "__main__":
    print("Generating police counter move...")
    try:
        result = police_counter()
        print("Success! Response JSON:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")
