# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
INDEXOPT      ?= -i# set to nothing to not override index.rst
GENOPTS       ?=# possible extra options for APIDOCGEN command
APIDOCGEN     ?= sphinx-autodoc
SOURCEDIR     = .
BUILDDIR      = _build
PACKAGE_NAME  = serpcord

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

cleangen:
	@rm -r generated && mkdir generated

gen:
	@$(APIDOCGEN) -s "$(SOURCEDIR)" $(GENOPTS) $(INDEXOPT) $(PACKAGE_NAME)

cleanall: clean cleangen

.PHONY: help cleanall cleangen gen Makefile


# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
