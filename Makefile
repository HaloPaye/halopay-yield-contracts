.PHONY: test-contracts test-agent simulate build-wasm lint

test-contracts:
	cd contracts && cargo test

test-agent:
	cd agent && pytest

simulate:
	cd agent && python src/main.py --mode simulation

build-wasm:
	soroban contract build

lint:
	cd agent && black src/ tests/ && flake8 src/ tests/ && mypy src/ tests/
