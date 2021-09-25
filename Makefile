# Local repo management
clean:
	rm -rf **/__pycache__ **/.pytest_cache/

# Type checking using mypy
typecheck:
	mypy -p mockitup --strict
typecheck-report:
	mypy -p mockitup --strict --html-report mypy_report

# Ensuring examples validity
make run-examples:
	pytest examples/ -c examples/pytest.ini