PYTHON ?= python
WORK ?= .work

.PHONY: experiment build serve test
experiment:
	$(PYTHON) scripts/experiment.py --cache $(WORK)/cache
build: experiment
	$(PYTHON) -m mkdocs build --strict --site-dir $(WORK)/site
serve: experiment
	$(PYTHON) -m mkdocs serve
test:
	$(PYTHON) -m unittest discover -s tests -v
