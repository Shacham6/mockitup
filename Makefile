# Local repo management
clean:
	rm -rf **/__pycache__ **/.pytest_cache/

# Type checking using mypy
typecheck:
	poetry run mypy -p mockitup --strict

typecheck-report:
	poetry run mypy -p mockitup --strict --html-report mypy_report

# Ensuring examples validity
run-examples:
	poetry run pytest examples/ -c examples/pytest.ini

tests:
	poetry run pytest tests/

check: | typecheck tests run-examples
