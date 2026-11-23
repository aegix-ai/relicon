# Relicon. Zero keys needed for every target except a real-provider render.
SHELL := /bin/bash
VENV  := .venv
PY    := $(VENV)/bin/python
RELICON := $(VENV)/bin/relicon
PNPM  := $(shell command -v pnpm || echo "npx -y pnpm@9.15.0")

.PHONY: setup test test-fast demo demo-loop dashboard eval schema clean

$(PY):
	@if command -v uv >/dev/null; then uv venv -q -p 3.12 $(VENV); else python3 -m venv $(VENV); fi

setup: $(PY)
	@if command -v uv >/dev/null; then VIRTUAL_ENV=$(VENV) uv pip install -q -e "engine[dev,postgres]"; \
	 else $(PY) -m pip install -q -e "engine[dev,postgres]"; fi

test: setup
	cd engine && ../$(PY) -m pytest -q

test-fast: setup
	cd engine && ../$(PY) -m pytest -q -m "not integration"

schema: setup
	$(PY) -m relicon.genome.export

# Full loop with mock providers + simulated market, then the dashboard.
demo: setup
	@bash scripts/demo.sh

# Headless loop only (used by CI).
demo-loop: setup
	$(RELICON) demo

dashboard: setup
	@bash scripts/dashboard.sh

eval: setup
	$(RELICON) eval

clean:
	rm -rf .relicon evals/raw
