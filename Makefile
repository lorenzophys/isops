MAIN_PATH=iops
TESTS_PATH=tests

.PHONY: clean
clean:
	find . -name '__pycache__' -exec rm -rf {} +
	rm -f .coverage
	rm -rf .pytest_cache

.PHONY: format
format:
	isort ${MAIN_PATH} ${TESTS_PATH}
	black ${MAIN_PATH} ${TESTS_PATH}

.PHONY: lint
lint:
	flake8 ${MAIN_PATH} ${TESTS_PATH}

.PHONY: test
test:
	pytest -vvv

.PHONY: coverage
coverage:
	pytest --no-cov-on-fail --cov-report term-missing --cov=${MAIN_PATH} tests/
