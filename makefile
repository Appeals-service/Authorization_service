# run_base:
# 	python otus_dj_pr/manage.py runserver 0.0.0.0:8000 --settings=otus_dj_pr.settings.base

create_revision:
	alembic -c src/alembic.ini revision --autogenerate

migrate:
	alembic -c src/alembic.ini upgrade head

downgrade:
	alembic -c src/alembic.ini downgrade -1


# run_polls_tests:
# 	python otus_dj_pr/manage.py test polls --settings=otus_dj_pr.settings.base

# create_su:
# 	python otus_dj_pr/manage.py createsuperuser --no-input --settings=otus_dj_pr.settings.base

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
