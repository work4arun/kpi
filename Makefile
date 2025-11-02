
.PHONY: help up down build restart logs migrate makemigrations superuser seed test lint clean shell

help:
	@echo "RTC KPI System - Makefile Commands"
	@echo "-----------------------------------"
	@echo "make up          - Start all services"
	@echo "make down        - Stop all services"
	@echo "make build       - Build Docker images"
	@echo "make restart     - Restart all services"
	@echo "make logs        - View logs"
	@echo "make migrate     - Run database migrations"
	@echo "make makemigrations - Create new migrations"
	@echo "make superuser   - Create Django superuser"
	@echo "make seed        - Load seed data"
	@echo "make test        - Run tests"
	@echo "make lint        - Run code linting"
	@echo "make clean       - Remove containers and volumes"
	@echo "make shell       - Open Django shell"

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

restart:
	docker compose restart

logs:
	docker compose logs -f web

migrate:
	docker compose exec web python manage.py migrate

makemigrations:
	docker compose exec web python manage.py makemigrations

superuser:
	docker compose exec web python manage.py createsuperuser

seed:
	docker compose exec web python manage.py shell < scripts/seed_data.py

test:
	docker compose exec web python manage.py test

lint:
	docker compose exec web flake8 apps/ rtc_kpi/

clean:
	docker compose down -v

shell:
	docker compose exec web python manage.py shell
