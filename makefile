
create_revision:
	alembic -c src/alembic.ini revision --autogenerate

migrate:
	alembic -c src/alembic.ini upgrade head

downgrade:
	alembic -c src/alembic.ini downgrade -1

run_tests:
	pytest .

run_tests_detail:
	pytest tests -s -vvv --setup-show tests

lint:
	ruff check

lint-fix:
	ruff check --fix

lint-format:
	ruff format

lint-isort:
	ruff check --select I

lint-isort-fix:
	ruff check --select I --fix

lint-base:
	ruff check --fix
	ruff check --select I --fix

check-hints:
	mypy .

dc-up:
	docker compose up -d --build

dc-down:
	docker compose down -v
