PYTHON ?= python
PIP ?= $(PYTHON) -m pip
PYTEST ?= $(PYTHON) -m pytest
STREAMLIT ?= $(PYTHON) -m streamlit

.PHONY: install test train evaluate app

install:
	$(PIP) install -r requirements.txt

test:
	$(PYTEST) -q

train:
	$(PYTHON) scripts/train.py

evaluate:
	$(PYTHON) scripts/evaluate.py

app:
	$(STREAMLIT) run app/Home.py
