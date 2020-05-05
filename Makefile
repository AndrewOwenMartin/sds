.PHONY: all build server clean sdist

#no quotes around my proj
project_name = sds
library_dir = sds
junk = *.toc *.log *.fls *.aux *.pdf *.tex *.fdb_latexmk *.out

all: $(project_name).pdf build sdist

venv: sds-venv/bin/activate activate

sds-venv/bin/activate:
	python3 -m venv sds-venv
	sed --in-place -e 's/(sds-venv)/(sds)/' sds-venv/bin/activate

activate:
	echo '#! /bin/echo Run like this ". activate" Error message from:' > activate
	echo 'source ./sds-venv/bin/activate' >> activate

COLS := $(shell tput cols)

$(project_name).tex: $(project_name).nw
	noweave -t4 -filter btdefn -delay -latex -index $(project_name).nw | cpif $(project_name).tex

$(project_name).pdf: $(project_name).tex
	latexmk -halt-on-error -pdf $(project_name).tex
	-pkill -hup mupdf

doc: $(project_name).pdf

# Use underscores everywhere except in the chunk name
%.py: $(project_name).nw
	notangle -R"$(subst _,-,$@)" -filter btdefn $(project_name).nw | cpif $@

project_files = \
	sds/__init__.py \
	sds/reducing.py \
	sds/variants.py \
	sds/standard.py \
	sds/test_sds.py \
	example/string_search.py

build: $(project_files)
	chmod 644 $(library_dir)/*.py
	black sds

requirements.txt:
	pip freeze > requirements.txt

server:
	when-changed -1 *.nw -c "max_print_line=$(COLS) make build && make doc && date"

test: build
	python -m unittest

sdist:
	rm -f dist/*.tar.gz
	python setup.py sdist

clean:
	rm -fv $(junk)
	rm -rf $(library_dir)
	git checkout $(library_dir)
	rm -rf dist
	git checkout dist
