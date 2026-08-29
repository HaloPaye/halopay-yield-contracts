import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.interfaces.cli import run_cli

if __name__ == "__main__":
    run_cli()
