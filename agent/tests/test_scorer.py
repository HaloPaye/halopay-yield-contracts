import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.scorer import evaluate_pool, score_pool

def test_scorer_deterministic():
    # Provide a fixed input and assert exact output
    res = score_pool(50000, 25000)
    assert res == 200.0
    
def test_evaluate_pool_disqualifies_liquidity():
    pool = {
        "id": "abc",
        "reserves": [
            {"asset": "native", "amount": "4000"},
            {"asset": "USDC:GABCD", "amount": "5000"}
        ]
    }
    score, reason = evaluate_pool(pool)
    assert score == 0.0
    assert reason == "LIQUIDITY_FLOOR_FAILED"
