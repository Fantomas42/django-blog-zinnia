# Makefile for Zinnia
#
# Aim to simplify development and release process
# Be sure you have run the buildout, before using this Makefile

NO_COLOR = \033[0m
COLOR	 = \033[32;01m

all: kwalitee test docs clean package

package:
	@echo "$(COLOR)* Creating source package for Zinnia$(NO_COLOR)"
	@python setup.py sdist

test:
	@echo "$(COLOR)* Launching the tests suite$(NO_COLOR)"
	@./bin/test

coverage:
	@echo "$(COLOR)* Generating coverage report$(NO_COLOR)"
	@./bin/cover

epydoc:
	@echo "$(COLOR)* Generating API documentation$(NO_COLOR)"
	@export DJANGO_SETTINGS_MODULE='demo.settings' && ./bin/api

sphinx:
	@echo "$(COLOR)* Generating Sphinx documentation$(NO_COLOR)"
	@./bin/docs
	@cp -r ./docs/build/html ./docs/

docs: coverage epydoc sphinx

kwalitee:
	@echo "$(COLOR)* Running pyflakes$(NO_COLOR)"
	@-./bin/pyflakes zinnia
	@echo "$(COLOR)* Running pep8$(NO_COLOR)"
	@-./bin/pep8 --count --exclude=tests.py,migrations zinnia

clean:
	@echo "$(COLOR)* Removing useless files$(NO_COLOR)"
	@find demo zinnia docs -type f \( -name "*.pyc" -o -name "\#*" -o -name "*~" \) -exec rm -f {} \;
	@rm -f \#* *~
	@rm -rf uploads

mrproper: clean
	@rm -rf docs/build/doctrees
	@rm -rf docs/build/html
	@rm -rf docs/html
	@rm -rf docs/coverage
	@rm -rf docs/api

