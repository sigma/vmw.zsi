#!/usr/bin/env python
#
# $Id$

VERSION="0.10.0"
CVS=0

from distutils.core import setup, Command, Extension
from SOAPpy import SOAP

url="http://pywebsvcs.sf.net/"

long_description="SOAPpy provides tools for building SOAP clients and servers.  For more information see " + url


if CVS:
    import time
    VERSION += "_CVS_"  + time.strftime('%Y_%m_%d')


setup(name="SOAPpy",
      version=VERSION,
      description="SOAP Services for Python",
      maintainer="Gregory Warnes",
      maintainer_email="gregory_r_warnes@groton.pfizer.com",
      url = url,
      long_description=long_description,
      packages=['SOAPpy','SOAPpy/wstools']
     )

