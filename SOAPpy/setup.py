from distutils.core import setup

url="http://pywebsvcs.sf.net/"

long_description="SOAPpy provides tools for building SOAP clients and servers.  For more information see " + url

setup(name="SOAPpy",
      version="0.9.7",
      description="SOAP Services for Python",
      author="Cayce Ullman, Brian Matthews, Gregory Warnes, Christopher Blunck",
      maintainer="Gregory Warnes",
      maintainer_email="gregory_r_warnes@groton.pfizer.com",
      url = url,
      long_description=long_description,
      packages=['SOAPpy',],
     )

