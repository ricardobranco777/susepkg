FILES=susepkg.py
BIN=susepkg

.PHONY: all
all: flake8 pylint mypy black

.PHONY: flake8
flake8:
	@flake8 --ignore=E501 $(FILES)

.PHONY: pylint
pylint:
	@pylint $(FILES)

.PHONY: mypy
mypy:
	@for f in $(FILES) ; do mypy $$f ; done

.PHONY: black
black:
	@black --check $(FILES)

.PHONY: install
install:
	install -m 0755 $(BIN) $(HOME)/bin/

.PHONY: uninstall
uninstall:
	cd $(HOME)/bin ; rm -f $(BIN)
