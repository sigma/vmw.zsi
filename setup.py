#! /usr/bin/env python
# $Header$
import sys
try:
    from setuptools import setup
    hasSetuptools = True
except ImportError:
    from distutils.core import setup
    hasSetuptools = False

_url = "http://pywebsvcs.sf.net/"

import ConfigParser
cf = ConfigParser.ConfigParser()
cf.read('setup.cfg')
major = cf.getint('version', 'major')
minor = cf.getint('version', 'minor')
patchlevel = cf.getint('version', 'patchlevel')
candidate = cf.getint('version', 'candidate')
alpha = cf.getint('version', 'alpha')
beta = cf.getint('version', 'beta')

_version = "%d.%d" % ( major, minor )
if patchlevel:
    _version += '.%d' % patchlevel
if candidate:
    _version += '_rc%d' % candidate
elif alpha:
    _version += '_a%d' % alpha
elif beta:
    _version += '_b%d' % beta

try:
    open('vmw/ZSI/version.py', 'r').close()
except:
    print 'vmw/ZSI/version.py not found; run "make"'
    sys.exit(1)

_packages = [ "vmw.ZSI", "vmw.ZSI.generate", "vmw.ZSI.wstools"]

if sys.version_info[0:2] >= (2, 4):
    _packages.append("vmw.ZSI.twisted")


# setuptools specific logic
additional_params = {}
if hasSetuptools:
    additional_params['entry_points'] = {
        'console_scripts': [
            'wsdl2py = vmw.ZSI.generate.commands:wsdl2py',
        ],
    }
    additional_params['setup_requires'] = [ "setuptools >= 0.6c3", ]
else:
    additional_params['scripts'] = ["scripts/wsdl2py",]

setup(
    name="vmw.ZSI",
    version=_version,
    license="Python",
    packages=_packages,
    namespace_packages = ['vmw',],
    description="Zolera SOAP Infrastructure -- VMware edition",
    author="Rich Salz, et al",
    author_email="rsalz@datapower.com",
    maintainer="Rich Salz, et al",
    maintainer_email="pywebsvcs-talk@lists.sf.net",
    url=_url,
    long_description="For additional information, please see " + _url,
    **additional_params
)
