clean:
	rm -rf **/__pycache__ **/.pytest_cache/

typecheck:
	mypy -p mockitup --strict
typecheck-report:
	mypy -p mockitup --strict --html-report mypy_report