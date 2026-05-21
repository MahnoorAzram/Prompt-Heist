def run_police_interrogation(score: int) -> str:
    """Evaluate the player's prompt score and return an interrogation response.

    Called AFTER the Prompt Evaluator and BEFORE the Heist Simulator.

    Args:
        score: The total prompt score from the Prompt Evaluator (0-50 range).

    Returns:
        A string: a threatening warning if the score is weak, or "Proceed" if acceptable.
    """
    if score < 30:
        return "Surrender. Your prompt is weak. You are going to fail. Do you understand?"
    return "Proceed"
