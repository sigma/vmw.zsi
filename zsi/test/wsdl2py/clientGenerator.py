import os, os.path
import shutil, sys
from ZSI import wsdl2python
from ZSI.wstools.WSDLTools import WSDLReader
from ZSI.wstools.TimeoutSocket import TimeoutError

from helperInterface import WriteHLSModule


class ClientGenerator:

    def getModule(self, serviceName, serviceLoc, codePath='.'):
        
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
        fd = open(path, 'w')
        fd.write('__all__= [\n')
        fd.write('          ]\n')
        fd.close()

    def updateInit(self, fname, module):
        fd = open(fname, 'r')
        lines = fd.readlines()
        fd.close()
            # isn't called unless initial import failed,
            # so there won't be duplicates 
        fd = open(fname, 'w')
        fd.write('__all__= [\n')
        for line in lines[1:-1]:
            fd.write(line)
        fd.write('         "%s.py",\n' % module)
        fd.write('          ]\n')
        fd.close()
