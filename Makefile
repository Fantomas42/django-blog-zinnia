# Makefile for Zinnia
#
# Aim to simplify development and release process
# Be sure you have run the buildout, before using this Makefile

NO_COLOR	= \033[0m
COLOR	 	= \033[32;01m
SUCCESS_COLOR	= \033[35;01m

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

sphinx:
	@echo "$(COLOR)* Generating Sphinx documentation$(NO_COLOR)"
	@./bin/docs

docs: coverage sphinx

kwalitee:
	@echo "$(COLOR)* Running pyflakes$(NO_COLOR)"
	@./bin/pyflakes zinnia
	@echo "$(COLOR)* Running pep8$(NO_COLOR)"
	@./bin/pep8 --count --show-source --show-pep8 --statistics --exclude=migrations zinnia
	@echo "$(SUCCESS_COLOR)* No kwalitee errors, Congratulations ! :)$(NO_COLOR)"

translations:
	@echo "$(COLOR)* Generating english translation$(NO_COLOR)"
	@cd zinnia && ../bin/demo makemessages --extension=.html,.txt -l en
	@echo "$(COLOR)* Pushing translation to Transifex$(NO_COLOR)"
	@rm -rf .tox
	@tx push -s
	@echo "$(COLOR)* Remove english translation$(NO_COLOR)"
	@rm -rf zinnia/locale/en/

2to3:
	@echo "$(COLOR)* Checking Py3 code$(NO_COLOR)"
	@2to3 -x future -x dict -x map -x xrange -x imports -x import -x urllib -x print -x input zinnia/

clean:
	@echo "$(COLOR)* Removing useless files$(NO_COLOR)"
	@find demo zinnia docs -type f \( -name "*.pyc" -o -name "\#*" -o -name "*~" \) -exec rm -f {} \;
	@rm -f \#* *~
	@rm -rf uploads
	@rm -rf .tox

mrproper: clean
	@rm -rf docs/build/doctrees
	@rm -rf docs/build/html
	@rm -rf docs/coverage

