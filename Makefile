
help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build-docker:
	docker build .

build-kubernetes:
	docker build -f _infra/docker/Dockerfile .

build:
	pipenv install --dev

lint:
	pipenv run isort .
	pipenv run black --line-length 120 .
	pipenv run flake8

lint-check:
	pipenv run isort --check-only .
	pipenv run black --line-length 120 --check .
	pipenv run flake8

test: lint-check
	pipenv run pytest

start:
	APP_SETTINGS=DevelopmentConfig pipenv run ./docker-entrypoint.sh

docker:
	docker build . -t sdcplatform/ras-rm-auth-service:latest
