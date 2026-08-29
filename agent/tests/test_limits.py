import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.scorer import evaluate_pool

def test_limits_disqualifies_unknown_assets():
    pool = {
        "id": "def",
        "reserves": [
            {"asset": "UNKNOWN:GXYZ", "amount": "10000"},
            {"asset": "native", "amount": "10000"}
        ]
    }
    score, reason = evaluate_pool(pool)
    assert score == 0.0
    assert reason == "UNKNOWN_ASSETS"
