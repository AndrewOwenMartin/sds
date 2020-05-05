.PHONY: all build server clean sdist

#no quotes around my proj
project_name = sds
library_dir = sds
junk = *.toc *.log *.fls *.aux *.pdf *.tex *.fdb_latexmk *.out

all: $(project_name).pdf build sdist

COLS := $(shell tput cols)

$(project_name).tex: $(project_name).nw
	noweave -t4 -filter btdefn -delay -latex -index $(project_name).nw | cpif $(project_name).tex

$(project_name).pdf: $(project_name).tex
	latexmk -halt-on-error -pdf $(project_name).tex
	-pkill -hup mupdf

doc: $(project_name).pdf

# Use underscores everywhere except in the chunk name
%.py: $(project_name).nw
	notangle -R"$(subst _,-,$@)" -filter btdefn $(project_name).nw | cpif $(library_dir)/$@

project_files = \
	__init__.py \
	reducing.py \
	variants.py \
	standard.py \
	test_sds.py

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
