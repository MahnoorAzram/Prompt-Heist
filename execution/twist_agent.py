import random


# Pool of twist templates — each affects next-mission difficulty or constraints
_TWIST_TEMPLATES = [
    "Twist: Next mission has double guards patrolling the vault room, increasing alert rate.",
    "Twist: Security cameras in the next mission are upgraded to infrared — standard jammers won't work.",
    "Twist: An undercover agent has infiltrated your crew. One operative's loyalty is uncertain next round.",
    "Twist: The next vault uses biometric + voice authentication — your crew needs a live hostage to proceed.",
    "Twist: Police response time is halved next mission due to a new rapid-deployment unit.",
    "Twist: A rival crew is targeting the same objective next mission — expect interference.",
    "Twist: Power grid instability means your tech operative's gadgets have a 50% failure chance.",
    "Twist: The next target has a silent alarm already tripped — you start at alarm level 2.",
    "Twist: An informant leaked your entry plan. The east wing is now a kill-zone.",
    "Twist: Hostage negotiators arrive early next mission — you lose ground floor leverage.",
    "Twist: Next mission's vault has a time-lock that resets every 3 minutes.",
    "Twist: A media helicopter is circling — any rooftop movement is instantly reported.",
]


def run_twist_agent(score: int, heist_outcome: dict) -> str:
    """Generate a dynamic twist that affects the next mission.

    Called AFTER the Heist Simulator and BEFORE the Difficulty Calibrator.

    Args:
        score: The total prompt score from the Prompt Evaluator.
        heist_outcome: The dict returned by the Heist Simulator (simulate_phase).

    Returns:
        A short twist string describing an unexpected rule change for the next mission.
    """
    # Use score + outcome to deterministically bias the twist severity
    # Lower scores / failed phases → harsher twists (earlier in the list)
    phase_success = heist_outcome.get("phase_success", True) if isinstance(heist_outcome, dict) else True
    if score < 30 or not phase_success:
        # Pick from the harsher half
        twist = random.choice(_TWIST_TEMPLATES[:6])
    else:
        # Pick from the full pool
        twist = random.choice(_TWIST_TEMPLATES)
    return twist
