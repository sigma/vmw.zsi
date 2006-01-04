#! /usr/bin/env python
# $Header$
import sys
from distutils.core import setup

_url = "http://pywebsvcs.sf.net/"

import ConfigParser
cf = ConfigParser.ConfigParser()
cf.read('setup.cfg')
major = cf.getint('version', 'major')
minor = cf.getint('version', 'minor')
patchlevel = cf.getint('version', 'patchlevel')
candidate = cf.getint('version', 'candidate')

_version = "%d.%d" % ( major, minor )
if patchlevel:
    _version += '.%d' % patchlevel
if candidate:
    _version += '_rc%d' % candidate

try:
    open('ZSI/version.py', 'r').close()
except:
    print 'ZSI/version.py not found; run "make"'
    sys.exit(1)

setup(
    name="ZSI",
    version=_version,
    license="Python",
    packages=[ "ZSI", "ZSI.generate", "ZSI.wstools"],
    scripts=["scripts/wsdl2py.py", "scripts/wsdl2dispatch.py"],
    description="Zolera SOAP Infrastructure",
    author="Rich Salz, et al",
    author_email="rsalz@datapower.com",
    maintainer="Rich Salz, et al",
    maintainer_email="pywebsvcs-talk@lists.sf.net",
    url=_url,
    long_description='For additional information, please see ' + _url
)
