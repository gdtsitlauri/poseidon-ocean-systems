.PHONY: setup experiments test clean

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

experiments:
	python -m src.poseidon_trident.run_all

test:
	pytest -q

clean:
	rm -rf .pytest_cache
