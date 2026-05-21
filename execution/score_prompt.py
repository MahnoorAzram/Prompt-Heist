import os
import json
import datetime
import requests
from dotenv import load_dotenv

def score_prompt(player_prompt: str):
    # Load environment variables from .env file
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(env_path)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Error: GEMINI_API_KEY not found in .env")

    # Load system prompt from prompt_evaluator.md
    directives_path = os.path.join(os.path.dirname(__file__), '..', 'directives', 'prompt_evaluator.md')
    
    if os.path.exists(directives_path):
        with open(directives_path, 'r', encoding='utf-8') as f:
            prompt_evaluator_content = f.read()
        
        # Extract the prompt instructions (from "You are an expert heist plan evaluator..." to the end)
        # We can clean it up or use it as is.
        # Let's extract everything starting from the first "You are an expert..." line.
        lines = prompt_evaluator_content.split('\n')
        system_prompt_lines = []
        started = False
        for line in lines:
            # We want to skip the "Agent 1 Name" and "Model dropdown" lines
            if "You are an expert heist plan evaluator" in line:
                started = True
            if started:
                system_prompt_lines.append(line)
        
        system_prompt = '\n'.join(system_prompt_lines).strip()
    else:
        # Fallback system prompt if the file is missing
        print("Warning: directives/prompt_evaluator.md not found, using embedded system prompt.")
        system_prompt = """You are an expert heist plan evaluator for a strategy game called Prompt Heist.

A player is acting as The Professor — a criminal mastermind planning a bank heist.
Their team of 4 agents is inside the bank:
- KHATTAK SAHAB: controls hostages, ground floor
- KARDAR: physical security, stairwells  
- PINKY: vault specialist
- KHOKAAR: tech expert, cameras

The player writes orders for their team.
You evaluate the quality of those orders.

EVALUATION CRITERIA:

CLARITY (0-25)
Can the team understand exactly what to do?
25 = crystal clear, no ambiguity
15 = mostly clear, minor gaps
5 = unclear, team confused
0 = completely meaningless

SPECIFICITY (0-25)
Are names, locations, timing, roles defined?
25 = who, what, where, when all specified
15 = some details missing
5 = very vague
0 = no specifics at all

FEASIBILITY (0-25)
Is this physically and logically possible?
25 = completely realistic
15 = possible but risky
5 = unlikely to work
0 = impossible

CREATIVITY (0-25)
Is this tactically smart and unexpected?
25 = brilliant, police won't expect this
15 = decent tactic
5 = obvious approach
0 = no tactical thinking

SCORING OUTCOMES:
81-100: Perfect execution. Team succeeds completely.
61-80: Success with minor complication.
41-60: Partial success. Something goes wrong.
21-40: Failure. Team member in danger.
0-20: Complete failure. Team member caught.

CURRENT MISSION CONTEXT:
The team is inside the Central Reserve Bank of Verano City.
Target: foreign currency vault on floor 2.
12 hostages secured on ground floor.
Police surrounding outside.
Time pressure is high.

Return ONLY this JSON. Nothing else. No explanation. No markdown. Just JSON.

{
  "clarity": <0-25>,
  "specificity": <0-25>,
  "feasibility": <0-25>,
  "creativity": <0-25>,
  "total": <0-100>,
  "grade": "<PERFECT|SUCCESS|PARTIAL|FAILURE|CRITICAL>",
  "feedback": "<one specific sentence about main weakness or strength>",
  "team_action": "<what the team actually does as a result — 2 sentences, present tense, cinematic>",
  "team_caught": "<null OR berlin OR tokyo OR nairobi OR rio — only if total below 30>",
  "vault_delta": <number 0-25>,
  "police_alert_delta": <number -1 to 2>
}"""

    # We try multiple models in case of quota issues (e.g. gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash)
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
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            # print(f"Attempting API call using {model}...")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            # Log raw response for debugging
            traces_dir = os.path.join(os.path.dirname(__file__), '..', 'traces')
            os.makedirs(traces_dir, exist_ok=True)
            timestamp = datetime.datetime.utcnow().isoformat().replace(':', '-')
            log_path = os.path.join(traces_dir, f"score_prompt_raw_{model}_{timestamp}.json")
            with open(log_path, 'w', encoding='utf-8') as log_f:
                log_f.write(response.text)
            
            if response.status_code == 200:
                result = response.json()
                text_response = result['candidates'][0]['content']['parts'][0]['text']
                # Parse to ensure it is valid JSON
                json_data = json.loads(text_response.strip())
                return json_data
            else:
                last_error = f"Model {model} returned status {response.status_code}: {response.text}"
        except Exception as e:
            last_error = f"Model {model} failed with exception: {str(e)}"
            
    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

if __name__ == "__main__":
    test_prompt = (
        "Rio disable cameras on floor 2. Nairobi "
        "start biometric scan. Tokyo block stairwell. "
        "Berlin keep hostages calm."
    )
    
    print("Evaluating player prompt...")
    print(f"Input prompt: '{test_prompt}'\n")
    
    try:
        score = score_prompt(test_prompt)
        print("Success! Response JSON:")
        print(json.dumps(score, indent=2))
    except Exception as e:
        print(f"Error: {e}")
