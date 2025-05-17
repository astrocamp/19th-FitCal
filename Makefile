runserver:
	uv run manage.py runserver

runserver-prod:
	uv run python manage.py collectstatic --noinput && DEBUG=False uv run manage.py runserver

makemigrations:
	uv run manage.py makemigrations

migrate:
	uv run manage.py migrate

showmigrations:
	uv run manage.py showmigrations

shell:
	uv run manage.py shell

dbshell:
	uv run manage.py dbshell