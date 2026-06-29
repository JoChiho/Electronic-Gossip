.PHONY: install install-dev lint typecheck test run build clean

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

lint:
	ruff check bagua tests scripts

typecheck:
	mypy bagua

test:
	pytest tests/ -v

run:
	python -m bagua

build:
	pip install -r requirements-build.txt
	pip install -e .
	pyinstaller packaging/bagua.spec --noconfirm --clean
	pyinstaller packaging/bagua-gui.spec --noconfirm --clean

clean:
	python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"