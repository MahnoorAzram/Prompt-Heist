import os
import json
import requests
from dotenv import load_dotenv

def generate_crisis(player_prompt: str):
    # Load environment variables from .env file
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(env_path)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Error: GEMINI_API_KEY not found in .env")

    # Load system prompt from crisis_generator.md
    directives_path = os.path.join(os.path.dirname(__file__), '..', 'directives', 'crisis_generator.md')

    if os.path.exists(directives_path):
        with open(directives_path, 'r', encoding='utf-8') as f:
            crisis_generator_content = f.read()
        # Use the whole file as system prompt
        system_prompt = crisis_generator_content.strip()
    else:
        raise FileNotFoundError("directives/crisis_generator.md not found")

    # Try multiple models in case of quota issues (e.g., gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash)
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
            "system_instruction": {
                "parts": {
                    "text": system_prompt
                }
            },
            "contents": [
                {
                    "parts": [
                        {
                            "text": player_prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }

        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
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
    player_prompt = """
    situation: Team moving toward vault, 2 guards nearby
    difficulty: medium
    active_members: KHATTAK SAHAB, KARDAR, PINKY, KHOKAAR
    last_crisis: None
    Generate a crisis now.
    """
    print("Generating crisis...")
    try:
        result = generate_crisis(player_prompt)
        print("Success! Crisis JSON:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")
