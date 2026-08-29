import argparse
import sys
import os
import time

# Ensure we can import from src regardless of where the script is run from
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.logger import log_event
from src.data_fetcher import fetch_liquidity_pools
from src.scorer import evaluate_pool
from src.contract_client import submit_allocation

def main():
    if not os.environ.get("AGENT_SECRET_KEY"):
        sys.exit("CRITICAL ERROR: AGENT_SECRET_KEY environment variable is missing. Cannot boot.")

    parser = argparse.ArgumentParser(description="HaloPay Yield Agent")
    parser.add_argument("--mode", type=str, default="simulation", choices=["simulation", "proposal", "live"])
    args = parser.parse_args()

    log_event(args.mode, "INFO", "STARTUP", message="HaloPay Yield Agent started.")
    
    while True:
        start_time = time.time()
        
        pools = fetch_liquidity_pools()
        
        if pools is None:
            # Sleep and retry handled by fetcher / loop timing
            pass
        else:
            best_score = 0.0
            best_pool_id = None
            
            for pool in pools:
                if "reserves" not in pool:
                    log_event(args.mode, "ERROR", "PARSE_ERROR", action="DISCARD_POOL", pool_id=pool.get("id"))
                    continue
                    
                score, reason = evaluate_pool(pool)
                if reason:
                    log_event(args.mode, "DEBUG", "POOL_DISQUALIFIED", pool_id=pool.get("id"), reason=reason)
                    continue
                    
                if score > best_score:
                    best_score = score
                    best_pool_id = pool.get("id")
                    
            if best_score < 1.5:
                log_event(args.mode, "INFO", "NO_ACTION", message=f"Best score {best_score} is below threshold. Doing nothing.")
            else:
                log_event(args.mode, "INFO", "DECISION_RECORDED", pool_id=best_pool_id, score=best_score, decision="ALLOCATE")
                if args.mode == "simulation":
                    log_event(args.mode, "INFO", "SIMULATION_END", message="[SIMULATION] Decision recorded. No transactions submitted.")
                    sys.exit(0)
                else:
                    submit_allocation(args.mode, best_pool_id, 500)
                    
        elapsed = time.time() - start_time
        if elapsed > 60:
            log_event(args.mode, "WARNING", "LOOP_OVERRUN", elapsed=elapsed)
            time.sleep(1)
        else:
            time.sleep(60 - elapsed)

if __name__ == "__main__":
    main()
