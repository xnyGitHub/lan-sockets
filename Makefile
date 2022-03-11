ifeq ($(shell python3 --version 2> /dev/null),)
    PYTHON = python
else
    PYTHON = python3
endif

lint:
	black src --line-length 120
	pylint src --max-line-length 120

server:
	$(PYTHON) -m src.server

player:
	$(PYTHON) -m src.player

