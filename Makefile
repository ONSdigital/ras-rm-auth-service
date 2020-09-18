
help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build-docker:
	docker build .

build-kubernetes:
	docker build -f _infra/docker/Dockerfile .

install:
	pipenv install --dev

lint:
	pipenv run flake8 --max-line-length=120 --max-complexity=10 --extend-ignore=E712 .

test: lint
	pipenv check
	pipenv run pytest

start:
	APP_SETTINGS=DevelopmentConfig pipenv run ./docker-entrypoint.sh

docker:
	docker build . -t sdcplatform/ras-rm-auth-service:latest
