ifeq ($(shell python3 --version 2> /dev/null),)
    PYTHON = python
else
    PYTHON = python3
endif

lint:
	black src --line-length 120
	flake8 src --max-line-length 120
