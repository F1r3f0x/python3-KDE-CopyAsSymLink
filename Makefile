.PHONY: install uninstall uninstall-old test coverage dist

test:
	python3 -m unittest discover -s tests -p "test_*.py"

coverage:
	@if command -v coverage >/dev/null 2>&1; then \
		coverage run -m unittest discover -s tests -p "test_*.py" && coverage report -m; \
	elif python3 -m coverage --version >/dev/null 2>&1; then \
		python3 -m coverage run -m unittest discover -s tests -p "test_*.py" && python3 -m coverage report -m; \
	else \
		echo "Error: 'coverage' is not installed."; \
		echo "Install it via your package manager or pip, for example:"; \
		echo "  Arch/CachyOS:  sudo pacman -S python-coverage"; \
		echo "  Ubuntu/Debian: sudo apt install python3-coverage"; \
		echo "  pip:           pip install coverage"; \
		exit 1; \
	fi


install:
	sh install.sh --install

uninstall:
	sh install.sh --uninstall

uninstall-old:
	sh uninstall-old.sh

dist:
	zip -r PasteAsSymLink.zip \
		pasteassymlink.py \
		plabin-dolphin-pasteassymlink.desktop \
		sys-plabin-dolphin-pasteassymlink.desktop \
		install.sh \
		uninstall-old.sh \
		Makefile \
		README.MD \
		LICENSE.txt