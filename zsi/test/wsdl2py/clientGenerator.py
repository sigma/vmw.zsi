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
        if not os.path.exists(codePath + os.sep + '__init__.py'):
            self.createInit(codePath + os.sep + '__init__.py')

        if section:
            cp = ConfigParser.ConfigParser()
            cp.read(configFileName)
            path = cp.get(section, serviceName)
        else:
            path = explicitPath
        sys.path.append(codePath)
        return path


    def getModule(self, configFileName, section, serviceName,
                  codePath='.', explicitPath=None):

        moduleName = wsdl2python.nonColonizedName_to_moduleName(serviceName)
        try:
            service = __import__(moduleName + '_services')
        except ImportError:
            path = self.setUp(configFileName, section, serviceName, codePath,
                       explicitPath)

            self.generateCode(path, codePath)
            service = __import__(moduleName + '_services')
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
        for filename in glob.glob('test_*.py'):
            fd.write('        "%s",\n' % filename)
        fd.write('        ]\n')
        fd.close()
