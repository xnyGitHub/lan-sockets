ifeq ($(shell python3 --version 2> /dev/null),)
    PYTHON = python
else
    PYTHON = python3
endif

lint:
	pylint src --max-line-length 120
	black src --line-length 120
	flake8 src --max-line-length 120
