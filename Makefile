ifeq ($(shell python3 --version 2> /dev/null),)
    PYTHON = python
else
    PYTHON = python3
endif

lint:
	black src --line-length 120
	mypy src --disallow-untyped-defs --check-untyped-defs --show-error-codes
	pylint --rcfile .pylintrc  --max-line-length 120 --fail-under 9 src

server:
	$(PYTHON) -m src.server

player:
	$(PYTHON) -m src.player

