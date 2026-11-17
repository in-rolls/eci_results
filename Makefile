.PHONY: fetch wayback parse build byelections validate test lint

# Download every input in data/source.json and check its SHA-256.
fetch:
	uv run python -m eci_results.fetch

# Re-fetch the archived ECI pages (slow; the pages are already in data/wayback/).
wayback:
	uv run python -m eci_results.fetch_wayback

parse:
	uv run python -m eci_results.parse_wayback

build: parse
	uv run python -m eci_results.build

# By-elections from ECI's index cards (data/raw/eci_reports/byelections/).
byelections:
	uv run python -m eci_results.byelections

validate:
	uv run python -m eci_results.validate

test:
	uv run pytest -q

lint:
	uv run black --check .
	uv run isort --check-only .
	uv run flake8 src tests
