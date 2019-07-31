# Run tests and generate coverage report.

coverage run --source=. -m unittest
coverage report -m
