import os
import json
from pathlib import Path
from dotenv import load_dotenv

def profile_player(scores):
    """Simple profiler that returns summary stats for given scores list."""
    if not isinstance(scores, list) or not scores:
        raise ValueError("scores must be a non‑empty list")
    avg = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    result = {
        "scores": scores,
        "average": avg,
        "max": max_score,
        "min": min_score,
        "summary": f"Average {avg:.1f}, range {min_score}-{max_score}"
    }
    return result

if __name__ == "__main__":
    # Test values per user request
    test_scores = [35, 72, 58, 84, 45]
    output = profile_player(test_scores)
    print(json.dumps(output, indent=2))
    # Save to traces folder
    traces_dir = Path(__file__).parent.parent / "traces"
    traces_dir.mkdir(exist_ok=True)
    (traces_dir / "trace_profiler_output.json").write_text(json.dumps(output, indent=2))
