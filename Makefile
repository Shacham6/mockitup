# Local repo management
clean:
	rm -rf **/__pycache__ **/.pytest_cache/

fix-format:
	poetry run yapf --recursive --in-place --parallel mockitup/ tests/ examples/

check-format:
	poetry run flake8 mockitup/ tests/ examples/

# Type checking using mypy
typecheck:
	poetry run mypy -p mockitup --strict

typecheck-report:
	poetry run mypy -p mockitup --strict --html-report mypy_report

# Ensuring examples validity
examples:
	poetry run pytest examples/ -c examples/pytest.ini

tests:
	poetry run pytest tests/

.PHONY: tests examples

check: | check-format typecheck tests examples
