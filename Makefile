
help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

run:
	DB_SCHEMA=ras_rm_oauth bash ./init_db.sh
	DB_SCHEMA=ras_rm_oauth DJANGO_SETTINGS_MODULE=ras_rm_auth_service.settings.default pipenv run gunicorn --bind 0.0.0.0:8040 --workers 8 ras_rm_auth_service.wsgi --pythonpath 'ras_rm_auth_service'

test: ## run all tests
	pipenv run ras_rm_auth_service/manage.py test authentication
