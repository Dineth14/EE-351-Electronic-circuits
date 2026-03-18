install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=power_electronics

dashboard:
	python -m power_electronics.dashboard.app

notebook:
	jupyter lab notebooks/

lint:
	pre-commit run --all-files

docs:
	sphinx-build docs/ docs/_build/
