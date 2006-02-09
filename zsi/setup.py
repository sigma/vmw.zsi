#! /usr/bin/env python
# $Header$
import sys
from distutils.command.build import build as _build
from distutils.command.build_py import build_py as _build_py
try:
    from setuptools import setup
except ImportError:
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

_twisted_packages = ['ZSI.twisted']
_twisted_options = [('twisted', None, 'build twisted packages')]

class build_py(_build_py):
    user_options = _build_py.user_options[:]
    user_options += _twisted_options
    boolean_options = _build.boolean_options[:]
    boolean_options.append(_twisted_options[0][0])

    def initialize_options(self):
        _build_py.initialize_options(self)
        self.twisted = False

    def run(self):
        if self.twisted:
            self.distribution.packages += _twisted_packages
        return _build_py.run(self)


class build(_build):
    user_options = _build.user_options[:]
    user_options += _twisted_options
    boolean_options = _build.boolean_options[:]
    boolean_options.append(_twisted_options[0][0])

    def initialize_options(self):
        _build.initialize_options(self)
        self.twisted = False

    def run(self):
        if self.twisted:
            self.distribution.packages += _twisted_packages
        return _build.run(self)


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
    long_description='For additional information, please see ' + _url,
    cmdclass={'build':build, 'build_py':build_py},
)
