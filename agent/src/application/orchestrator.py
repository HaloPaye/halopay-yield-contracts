import time
import sys
from src.config.logger import log_event
from src.infrastructure.data_fetcher import fetch_liquidity_pools
from src.domain.scorer import evaluate_pool
from src.infrastructure.contract_client import submit_allocation


def run_orchestrator(mode: str):
    log_event(mode, "INFO", "STARTUP", message="HaloPay Yield Agent started.")

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
                    log_event(
                        mode,
                        "ERROR",
                        "PARSE_ERROR",
                        action="DISCARD_POOL",
                        pool_id=pool.get("id"),
                    )
                    continue

                score, reason = evaluate_pool(pool)
                if reason:
                    log_event(
                        mode,
                        "DEBUG",
                        "POOL_DISQUALIFIED",
                        pool_id=pool.get("id"),
                        reason=reason,
                    )
                    continue

                if score > best_score:
                    best_score = score
                    best_pool_id = pool.get("id")

            if best_score < 1.5:
                log_event(
                    mode,
                    "INFO",
                    "NO_ACTION",
                    message=f"Best score {best_score} is below threshold. Doing nothing.",
                )
            else:
                log_event(
                    mode,
                    "INFO",
                    "DECISION_RECORDED",
                    pool_id=best_pool_id,
                    score=best_score,
                    decision="ALLOCATE",
                )
                if mode == "simulation":
                    log_event(
                        mode,
                        "INFO",
                        "SIMULATION_END",
                        message="[SIMULATION] Decision recorded. No transactions submitted.",
                    )
                    sys.exit(0)
                else:
                    if best_pool_id:
                        submit_allocation(mode, str(best_pool_id), 500)

        elapsed = time.time() - start_time
        if elapsed > 60:
            log_event(mode, "WARNING", "LOOP_OVERRUN", elapsed=elapsed)
            time.sleep(1)
        else:
            time.sleep(60 - elapsed)
