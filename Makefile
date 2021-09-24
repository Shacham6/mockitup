clean:
	rm -rf **/__pycache__ **/.pytest_cache/

typecheck:
	mypy -p mockitup.composer --strict
typecheck-report:
	mypy -p mockitup.composer --strict --html-report mypy_report