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
creates the directory where the code is placed
If the code has already been generated, it returns a
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
