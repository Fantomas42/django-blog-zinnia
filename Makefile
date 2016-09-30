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
	@echo "$(COLOR)* Running flake8$(NO_COLOR)"
	@./bin/flake8 --show-source --statistics zinnia
	@echo "$(SUCCESS_COLOR)* No kwalitee errors, Congratulations ! :)$(NO_COLOR)"

push-translations:
	@echo "$(COLOR)* Generating english translation$(NO_COLOR)"
	@cd zinnia && ../bin/demo makemessages --extension=html,xml,txt,py -l en
	@echo "$(COLOR)* Pushing source translation to Transifex$(NO_COLOR)"
	@tx push -s
	@echo "$(COLOR)* Removing source translation$(NO_COLOR)"
	@rm -rf zinnia/locale/en/

pull-translations:
	@echo "$(COLOR)* Pulling translations from Transifex$(NO_COLOR)"
	@tx pull -a -f --minimum-perc=50
	@echo "$(COLOR)* Compiling translations$(NO_COLOR)"
	@cd zinnia && ../bin/demo compilemessages

2to3:
	@echo "$(COLOR)* Checking Py3 code$(NO_COLOR)"
	@2to3 -x future -x dict -x map -x xrange -x imports -x import -x urllib -x print -x input zinnia/

clean:
	@echo "$(COLOR)* Removing useless files$(NO_COLOR)"
	@find demo zinnia docs -type f \( -name "*.pyc" -o -name "\#*" -o -name "*~" \) -exec rm -f {} \;
	@rm -f \#* *~
	@rm -rf uploads

mrproper: clean
	@rm -rf docs/build/doctrees
	@rm -rf docs/build/html
	@rm -rf docs/coverage
