import os
import requests
from dotenv import load_dotenv
import json
def simulate_phase(prompt_score: int, vault_progress: int, police_alert: int):
    """Call the Gemini API using the heist_simulator directive.
    Returns the JSON response from the simulator.
    """
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(env_path)
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError('GEMINI_API_KEY not found in .env')

    directives_path = os.path.join(os.path.dirname(__file__), '..', 'directives', 'heist_simulator.md')
    if not os.path.exists(directives_path):
        raise FileNotFoundError('heist_simulator.md not found')
    with open(directives_path, 'r', encoding='utf-8') as f:
        system_prompt = f.read().strip()

    user_prompt = f"""
    prompt_score: {prompt_score}
    vault_progress: {vault_progress}
    police_alert: {police_alert}
    Simulate the heist phase now.
    """
    models_to_try = ["gemini-1.5-flash","gemini-1.5-pro","gemini-2.5-flash","gemini-2.0-flash"]
    last_error = None
    import time, datetime, json
    attempts = 0
    max_attempts = 3
    for model in models_to_try:
        backoff = 5  # seconds
        while attempts < max_attempts:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {"system_instruction": {"parts": [{"text": system_prompt}]},
                      "contents": [{"parts": [{"text": user_prompt}]}],
                      "generationConfig": {"responseMimeType": "application/json"}}
            try:
                response = requests.post(url, json=payload, timeout=30)
                # Log raw response
                traces_dir = os.path.join(os.path.dirname(__file__), '..', 'traces')
                os.makedirs(traces_dir, exist_ok=True)
                timestamp = datetime.datetime.utcnow().isoformat().replace(":", "-")
                log_path = os.path.join(traces_dir, f"simulate_phase_raw_{model}_{timestamp}.json")
                with open(log_path, "w", encoding="utf-8") as log_f:
                    log_f.write(response.text)
                if response.status_code == 200:
                    result = response.json()
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    return json.loads(text.strip())
                elif response.status_code == 429:
                    # quota exceeded, backoff and retry
                    attempts += 1
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                else:
                    last_error = f"Model {model} returned {response.status_code}: {response.text}"
                    break
            except Exception as e:
                last_error = f"Model {model} exception: {e}"
                break
        attempts = 0  # reset attempts for next model
    raise RuntimeError(f"All models failed. Last error: {last_error}")

if __name__ == '__main__':
    output = simulate_phase(prompt_score=72, vault_progress=25, police_alert=20)
    print(json.dumps(output, indent=2))
    # Save to traces
    traces_dir = os.path.join(os.path.dirname(__file__), '..', 'traces')
    os.makedirs(traces_dir, exist_ok=True)
    with open(os.path.join(traces_dir, 'trace_simulator_output.json'), 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
