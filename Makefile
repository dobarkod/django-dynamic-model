SETUP=python setup.py

.PHONY: all build test coverage docs clean

all: build coverage docs

build:
	$(SETUP) build

test:
	cd testproject && python manage.py test testapp

coverage:
	cd testproject && coverage run manage.py test testapp && coverage html

upload: build coverage docs
	$(SETUP) sdist upload
