#!/usr/bin/env python

VERSION="0.9.9-pre6"
CVS=1

from distutils.core import setup, Command, Extension
from SOAPpy import SOAP

url="http://pywebsvcs.sf.net/"

long_description="SOAPpy provides tools for building SOAP clients and servers.  For more information see " + url


if CVS:
    import time
    VERSION += "-CVS-"  + time.strftime('%Y-%m-%d')


setup(name="SOAPpy",
      version=VERSION,
      description="SOAP Services for Python",
      maintainer="Gregory Warnes",
      maintainer_email="gregory_r_warnes@groton.pfizer.com",
      url = url,
      long_description=long_description,
      packages=['SOAPpy','SOAPpy/wstools']
     )

