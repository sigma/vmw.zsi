############################################################################
# David W. Robertson, LBNL
# See Copyright for copyright notice!
###########################################################################

import os, os.path
import shutil, sys
from ZSI import wsdl2python
from ZSI.wstools.WSDLTools import WSDLReader
from ZSI.wstools.TimeoutSocket import TimeoutError

from helperInterface import WriteHLSModule

"""
clientGenerator:  This module contains a class that
aids in the automatic generation of client code.  It
creates the directory where the code is placed, and
an __init__.py file, if they don't exist.  If
the code has already been generated, it returns a
reference to the module.  If not, it generates the
code in the given directory and returns a reference
to the module.
"""


class ClientGenerator:

    def getModule(self, serviceName, serviceLoc, codePath='.'):
        """Get a reference to the module corresponding to
           serviceName, generating code if necessary.
        """
        
        if not os.path.exists(codePath):
            os.mkdir(codePath)
        initPath = codePath + os.sep + '__init__.py'
        if not os.path.exists(initPath):
            self.createInit(initPath)

        if codePath not in sys.path:
            sys.path.append(codePath)

        helperModuleName = \
            wsdl2python.nonColonizedName_to_moduleName(serviceName) + \
                '_services_interface'
        try:
            helper = __import__(helperModuleName)
        except ImportError:
            self.generateCode(serviceLoc, codePath)
            helper = __import__(helperModuleName)
            self.updateInit(initPath, helperModuleName)
        return helper


    def generateCode(self, serviceLoc, codePath='.'):
        """Generate code in the codePath directory, given
           a WSDL location.
        """

        try:
            if serviceLoc[:7] == 'http://':
                wsdl = WSDLReader().loadFromURL(serviceLoc)
            else:
                wsdl = WSDLReader().loadFromFile(serviceLoc)
        except TimeoutError:
            print "connection timed out"
            sys.stdout.flush()
            return None
        currentPath = os.getcwd()
        os.chdir(codePath)
        wsm = WriteHLSModule(wsdl)
        wsm.write()
        os.chdir(currentPath)


    def createInit(self, path):
        """Create an __init__.py file"""

        fd = open(path, 'w')
        fd.write('__all__= [\n')
        fd.write('          ]\n')
        fd.close()

    def updateInit(self, fname, module):
        """Update an __init__.py file"""

        fd = open(fname, 'r')
        lines = fd.readlines()
        fd.close()
            # isn't called unless initial import failed,
            # so there won't be duplicates 
        fd = open(fname, 'w')
        fd.write('__all__= [\n')
        for line in lines[1:-1]:
            fd.write(line)

            # add reference to module
        fd.write('         "%s.py",\n' % module)
        fd.write('          ]\n')
        fd.close()
