import os, os.path
import shutil, sys
import ConfigParser, glob

from ZSI import wsdl2python
from ZSI.wstools.WSDLTools import WSDLReader
from ZSI.wstools.TimeoutSocket import TimeoutError


class ClientGenerator:

    def setUp(self, configFileName, section, serviceName, codePath,
              explicitPath):
        if not os.path.exists(codePath):
            os.mkdir(codePath)
        initPath = codePath + os.sep + '__init__.py'
        if not os.path.exists(initPath):
            self.createInit(initPath)

        if section:
            cp = ConfigParser.ConfigParser()
            cp.read(configFileName)
            path = cp.get(section, serviceName)
        else:
            path = explicitPath
        return path, initPath


    def getModule(self, configFileName, section, serviceName,
                  codePath='.', explicitPath=None):

        if codePath not in sys.path:
            sys.path.append(codePath)
        moduleName = \
            wsdl2python.nonColonizedName_to_moduleName(serviceName) + \
                '_services'
        try:
            service = __import__(moduleName)
        except ImportError:
            path, initPath = \
                self.setUp(configFileName, section, serviceName, codePath,
                           explicitPath)

            self.generateCode(path, codePath)
            service = __import__(moduleName)
            self.updateInit(initPath, moduleName)
        return service


    def generateCode(self, path, codePath='.'):
        try:
            if path[:7] == 'http://':
                wsdl = WSDLReader().loadFromURL(path)
            else:
                wsdl = WSDLReader().loadFromFile(path)
        except TimeoutError:
            print "connection timed out"
            sys.stdout.flush()
            return None
        currentPath = os.getcwd()
        os.chdir(codePath)
        codegen = wsdl2python.WriteServiceModule(wsdl)
        codegen.write()
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
