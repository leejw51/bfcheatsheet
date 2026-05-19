SHELL    := /bin/bash
ENV_NAME ?= bfcheatsheet
PY_VER   ?= 3.11
SRC      ?= .
OUT      ?= pdf

# Run a command inside the conda env without needing `conda activate` in make.
CONDA_RUN = conda run -n $(ENV_NAME) --no-capture-output

.DEFAULT_GOAL := help

.PHONY: help env install browsers convert clean distclean

help:
	@echo ""
	@echo "  bfcheatsheet — make targets"
	@echo "  ---------------------------"
	@echo "  make            show this menu"
	@echo "  make env        create conda env '$(ENV_NAME)' (python=$(PY_VER))"
	@echo "  make install    create env + install deps + Chromium"
	@echo "  make browsers   (re)install Playwright Chromium only"
	@echo "  make convert    convert HTML to PDF recursively (SRC=$(SRC) OUT=$(OUT))"
	@echo "  make clean      remove generated PDFs in $(OUT)/"
	@echo "  make distclean  also remove conda env '$(ENV_NAME)'"
	@echo ""
	@echo "  variables: ENV_NAME=$(ENV_NAME)  PY_VER=$(PY_VER)  SRC=<dir>  OUT=<dir>"
	@echo ""

env:
	@if ! command -v conda >/dev/null 2>&1; then \
		echo "error: conda not found in PATH. install Miniconda/Anaconda first."; exit 1; \
	fi
	@if ! conda env list | awk '{print $$1}' | grep -qx "$(ENV_NAME)"; then \
		echo ">> creating conda env '$(ENV_NAME)' (python=$(PY_VER))"; \
		conda create -y -n $(ENV_NAME) python=$(PY_VER); \
	else \
		echo ">> conda env '$(ENV_NAME)' already exists"; \
	fi

install:
	pip install -r requirements.txt

convert: browsers
	python html_to_pdf.py $(SRC) -o $(OUT)

browsers:
	python -m playwright install chromium

clean:
	rm -rf $(OUT)

distclean: clean
	-conda env remove -y -n $(ENV_NAME)
