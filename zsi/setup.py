#! /usr/bin/env python
# $Header$
import sys
from distutils.core import setup

_url = "http://pywebsvcs.sf.net/"

import ConfigParser
cf = ConfigParser.ConfigParser()
cf.read('setup.cfg')
_version = "%d.%d" % \
    ( cf.getint('version', 'major'), cf.getint('version', 'minor') )

try:
    open('ZSI/version.py', 'r').close()
except:
    print 'ZSI/version.py not found; run "make"'
    sys.exit(1)

setup(
    name="ZSI",
    version=_version,
    licence="Python",
    packages=[ "ZSI", "ZSI.wstools" ],
    description="Zolera SOAP Infrastructure",
    author="Rich Salz",
    author_email="rsalz@zolera.com",
    maintainer="Rich Salz",
    maintainer_email="rsalz@zolera.com",
    url=_url,
    long_description='For additional information, please see ' + _url
)
