
help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install:
	pipenv install --dev

lint:
	pipenv run flake8 --max-line-length=120 --max-complexity=10 .

test: lint
	pipenv check
	pipenv run pytest

run:
	FLASK_APP=run.py pipenv run flask run --port=8041

docker:
	docker build . -t sdcplatform/ras-rm-auth-service:latest
