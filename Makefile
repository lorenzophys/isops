MAIN_PATH=iops
TESTS_PATH=tests

.PHONY: clean
clean:
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '.DS_Store' -exec rm -rf {} +
	find . -name '.pytest_cache' -exec rm -rf {} +
	find . -name '.mypy_cache' -exec rm -rf {} +
	rm -f .coverage

.PHONY: format
format:
	isort ${MAIN_PATH} ${TESTS_PATH}
	black ${MAIN_PATH} ${TESTS_PATH}

.PHONY: lint
lint:
	flake8 ${MAIN_PATH} ${TESTS_PATH}
	mypy ${MAIN_PATH}

.PHONY: test
test:
	pytest -vvv

.PHONY: coverage
coverage:
	pytest --no-cov-on-fail --cov-report term-missing --cov=${MAIN_PATH} tests/
