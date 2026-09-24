.PHONY: install test lint dry run clean
install:  ; pip install -r requirements.txt pytest ruff
test:     ; python -m pytest -q
lint:     ; ruff check src tests --select E9,F63,F7,F82
dry:      ; DRY_RUN=1 python -m src.main
one:      ; DRY_RUN=1 ONLY_CATEGORIES=$(CAT) python -m src.main
run:      ; python -m src.main
clean:    ; rm -rf .httpcache __pycache__ src/__pycache__ .pytest_cache
