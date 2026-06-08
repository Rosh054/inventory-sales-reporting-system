.PHONY: up down seed test logs reset build

up:
	docker compose up -d --build

down:
	docker compose down

seed:
	docker compose exec backend python -m app.seed.seed_data

test:
	docker compose exec backend pytest tests/ -v

logs:
	docker compose logs -f

reset:
	docker compose down -v
	docker compose up -d --build
	@echo "Waiting for services..."
	@sleep 8
	docker compose exec backend python -m app.seed.seed_data

build:
	docker compose build
