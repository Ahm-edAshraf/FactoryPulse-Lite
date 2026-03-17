PYTHON := .venv/bin/python
PIP := .venv/bin/pip
PYTEST := .venv/bin/pytest
STREAMLIT := .venv/bin/streamlit

.PHONY: install test train app

install:
	$(PIP) install -r requirements.txt

test:
	PYTHONPATH=src $(PYTEST) -q

train:
	PYTHONPATH=src $(PYTHON) -m factorypulse.models.train_rul

app:
	PYTHONPATH=src $(STREAMLIT) run app/Home.py
