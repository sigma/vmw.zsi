#

# Change this to point to your Python2 exectuable
PYTHON = python

all:	rpm

ins:	ZSI/version.py	# install new version
	soup $(PYTHON) setup.py install

kit:	ver doc rpm	# make a kit

rpm:	ZSI/version.py
	$(PYTHON) setup.py bdist_rpm --python=$(PYTHON)

doc:			# build the docs
	$(MAKE) -C doc

ver:			# update the build number
	$(PYTHON) newver.py --incr --pyver --texver

.PHONY: all ins kit rpm doc ver

ZSI/version.py:		setup.cfg
	$(PYTHON) newver.py --pyver

doc/version.tex:	setup.cfg
	$(PYTHON) newver.py --texver
