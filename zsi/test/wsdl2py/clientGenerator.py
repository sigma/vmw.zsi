import os, os.path
import shutil, sys

from ZSI import wsdl2python
from ZSI.wstools.TimeoutSocket import TimeoutError

import utils

class ClientGenerator:

    def getModule(self, section, serviceName, subdirPath,
                 schemaOnly=False, explicitPath=None):
        sys.path.append(subdirPath)
        try:
            # fix
            service = __import__(serviceName + '_services')
        except ImportError:
            service = self.generateCode(section, serviceName, subdirPath,
                                        schemaOnly, explicitPath)
        return service


    def generateCode(self, section, serviceName, subdirPath,
                     schemaOnly, explicitPath):
        if not os.path.exists(subdirPath):
            os.mkdir(subdirPath)
        if not os.path.exists(subdirPath + os.sep + '__init__.py'):
            shutil.copy('test.init.py', subdirPath + os.sep + '__init__.py')
        if section:
            ch = utils.ConfigHandler()
            path = ch.get(section, serviceName)
        else:
            path = explicitPath
        try:
            wsdl = utils.setUpWsdl(path)
        except TimeoutError:
            print "connection timed out"
            sys.stdout.flush()
            return None
        codegen = wsdl2python.WriteServiceModule(wsdl)
        f_types, f_services = codegen.get_module_names()
        hasSchema = len(codegen._wa.getSchemaDict())

        if hasSchema:
            fd = open(subdirPath + os.sep + f_types + '.py', 'w+')
            codegen.write_service_types(f_types, fd)
            fd.close()

        """
            # necessary in this context?
        if schemaOnly:
            return True
        """

        fd = open(subdirPath + os.sep + f_services + '.py', 'w+')
        codegen.write_services(f_types, f_services, fd, hasSchema)
        fd.close()

        service = __import__(f_services)
        return service


