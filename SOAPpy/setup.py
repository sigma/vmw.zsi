from distutils.core import setup

url="http://pywebsvcs.sf.net/"

long_description="SOAPpy provides tools for building SOAP clients and servers.  For more information see " + url

from SOAPpy import SOAP

setup(name="SOAPpy",
      version=SOAP.__version__,
      description="SOAP Services for Python",
      maintainer="Gregory Warnes",
      maintainer_email="gregory_r_warnes@groton.pfizer.com",
      url = url,
      long_description=long_description,
      packages=['SOAPpy','SOAPpy/wstools'],
     )

