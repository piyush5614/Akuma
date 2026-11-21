.PHONY: help up down seed test lint e2e

help:
	@echo "FairFarm commands: up down seed test lint e2e"

up:
	docker compose up --build

down:
	docker compose down

seed:
	python backend/scripts/seed_demo.py

test:
	python -m pytest backend/tests

lint:
	python -m ruff check backend

e2e:
	python scripts/e2e_check.py

