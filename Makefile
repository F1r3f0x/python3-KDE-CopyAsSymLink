.PHONY: install uninstall uninstall-old test

test:
	python3 -m unittest discover -s tests -p "test_*.py"

install:
	sh install.sh --install

uninstall:
	sh install.sh --uninstall

uninstall-old:
	sh uninstall-old.sh