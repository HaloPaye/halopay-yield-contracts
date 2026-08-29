import argparse
import sys
import os

# Ensure we can import from src regardless of where the script is run from
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.application.orchestrator import run_orchestrator

def run_cli():
    if not os.environ.get("AGENT_SECRET_KEY"):
        sys.exit("CRITICAL ERROR: AGENT_SECRET_KEY environment variable is missing. Cannot boot.")

    parser = argparse.ArgumentParser(description="HaloPay Yield Agent")
    parser.add_argument("--mode", type=str, default="simulation", choices=["simulation", "proposal", "live"])
    args = parser.parse_args()

    run_orchestrator(args.mode)

if __name__ == "__main__":
    run_cli()
