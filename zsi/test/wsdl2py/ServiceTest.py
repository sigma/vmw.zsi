############################################################################
# Joshua R. Boverhof, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import os, sys, unittest
from ConfigParser import ConfigParser
from ZSI.wstools.WSDLTools import WSDLReader
from ZSI.wsdl2python import WriteServiceModule

"""Global Variables:
    CONFIG_FILE -- configuration file 
    CONFIG_PARSER -- ConfigParser instance
    DOCUMENT -- test section variable, specifying document style.
    LITERAL -- test section variable, specifying literal encodings.
    BROKE -- test section variable, specifying broken test.
    TESTS -- test section variable, whitespace separated list of modules.
    TRACEFILE -- file class instance.
"""
CONFIG_FILE = 'config.txt'
CONFIG_PARSER = ConfigParser()
DOCUMENT = 'document'
LITERAL = 'literal'
BROKE = 'broke'
TESTS = 'tests'
TRACEFILE = sys.stdout

CONFIG_PARSER.read(CONFIG_FILE)


class ConfigException(Exception):
    """Exception thrown when configuration settings arent correct.
    """
    pass

class TestException(Exception):
    """Exception thrown when test case isn't correctly set up.
    """
    pass

class ServiceTestCase(unittest.TestCase):
    """Must set these class variables typeModuleName, serviceModuleName,
       path, and schema.  moduleDict is filled in after modules are created.

       class variables:
           name -- configuration item, must be set in class.
           url_section -- configuration section, maps a test module name to an URL.
    """
    name = None
    url_section = 'WSDL'

    def __init__(self, methodName):
        """
        parameters:
           methodName -- 
        instance variables:
           _moduleDict -- module dictionary
           _port -- soap port, proxy rpc instance.
           _typeModuleName -- key to the generated type module
           _serviceModuleName -- key to the generated service module
           _section -- if set, do a runtime check that test is correctly indexed.
           _wsm -- WriteServiceModule instance
        """
        self._moduleDict = {}
        self._port = None
        self._typeModuleName = None
        self._serviceModuleName = None
        self._wsm = None
        self._section = None
        unittest.TestCase.__init__(self, methodName)

    def setUp(self):
        """Generate types and services modules if no record of them
           in the moduleDict variable.
        """
        if not self.url_section or not self.name:
            raise TestException, 'section(%s) or name(%s) not defined' %(self.url_section,self.name)
        if not self._isSetModules():
            if not CONFIG_PARSER.has_section(self.url_section):
                raise TestException, 'No such section(%s) in configuration file(%s)' \
                    %(self.url_section, CONFIG_FILE)
            testDir = os.getcwd()
            moduleDir = self._getModuleDirectory()
            try:
                os.mkdir(moduleDir)
            except OSError, ex:
                pass
            os.chdir(moduleDir)
            if moduleDir not in sys.path:
                sys.path.append(moduleDir)
            reader = WSDLReader()
            url = CONFIG_PARSER.get(self.url_section, self.name)
            wsdl = reader.loadFromURL(url)
            self._wsm = WriteServiceModule(wsdl)
            self._wsm.write(False)
            self._setModuleNames()
            os.chdir(testDir)
            locator = self._getLocator()
            self._port = self._getPort(locator)

    def _getPortOptions(self):
        kw = {}
        if CONFIG_PARSER.getboolean('configuration', 'tracefile'):
            kw['tracefile'] = TRACEFILE
        return kw

    def _getModuleDirectory(self):
            return os.getcwd() + '/stubs'

    def _getLocator(self):
        """Hack to get at the Locator name, it would be much easier
           if this information was directly available from the 
           WriteServiceModule instance.

           **Only expecting 1 service/WSDL, and 1 port/service.

           wsm -- WriteServiceModule instance
        """
        #XXX locatorName: Would be nice to have a method call to get this.
        serviceAdapter = self._getServiceAdapter()
        locatorName = '%sLocator' %serviceAdapter.getName()
        if self._moduleDict.has_key(self._serviceModuleName):
            sm = self._moduleDict[self._serviceModuleName]
            if sm.__dict__.has_key(locatorName):
                return sm.__dict__[locatorName]()
            raise TestException, 'No Locator class (%s), missing SOAP location binding?' %locatorName
        raise TestException, 'missing service module, possibly no WSDL service item?'

    def _getPort(self, locator):
        """Returns a rpc proxy port instance.
           **Only expecting 1 service/WSDL, and 1 port/service.

           locator -- Locator instance
        """
        portAdapter = self._getPortAdapter()
        #XXX methodName: Would be nice to have a method call to get this.
        methodName = 'get%s' %portAdapter.getBinding().getPortType().getName()
        callMethod = getattr(locator, methodName)
        return callMethod(**self._getPortOptions())

    def _getPortAdapter(self):
        """
           **Only expecting 1 service/WSDL, and 1 port/service.

           Hack to get at the Locator getPort method name, it would be much easier
           if this information was directly available from the 
           WriteServiceModule instance.

        """
        serviceAdapter = self._getServiceAdapter()
        portList = serviceAdapter.getPortList()
        if len(portList) != 1:
            raise TestException, 'Test framework expects service[%s] to define a single port, (%d) defined' \
                %(serviceAdapter.getName(), len(portList))
        return portList[0]

    def _getServiceAdapter(self):
        """
           **Only expecting 1 service/WSDL, and 1 port/service.

           Hack to get at the Locator getPort method name, it would be much easier
           if this information was directly available from the 
           WriteServiceModule instance.

        """
        serviceList = self._wsm._wa.getServicesList()
        if len(serviceList) != 1:
            raise TestException, 'Test framework expects WSDL to define a single service, (%d) defined' \
                %(len(serviceList))
        return serviceList[0]

    def _isSetModules(self):
        """Are the types/service modules already loaded?
        """
        if self._serviceModuleName: 
            return True
        return False

    def _setModuleNames(self):
        """set service and types modules key names, and import them.
        """
        self._typeModuleName, self._serviceModuleName = self._wsm.get_module_names()
        for name in (self._typeModuleName, self._serviceModuleName):
            exec('import %s' %name)
            self._moduleDict[name] = eval(name)

    def checkSection(self):
        """Should the section be checked? If I know about it.
        """
        return type(self._section) is str

    def checkPort(self, portAdapter, operationName):
        """Check if test is in correctly indexed in the configuration file, 
           port operation must conform to the bindings.  

           portAdapter -- ZSIPortAdapter instance
           operationName -- WSDL port operation name
           port -- WSDLTools.Port instance
        """
        port = portAdapter._port
        if self.checkSection():
            doc = CONFIG_PARSER.get(self.getSection(), DOCUMENT)
            lit = CONFIG_PARSER.get(self.getSection(), LITERAL)
            callinfo = callInfoFromWSDL(port, name)
            if doc and callinfo.style != 'document':
                raise ConfigException, 'operation(%s) is not document style' %name
            elif not doc and callinfo.style != 'rpc':
                raise ConfigException, 'operation(%s) is not rpc style' %name
            if lit is True and callinfo.encodingStyle != 'literal':
                raise ConfigException, 'operation(%s) is not literal encoding' %name
            if lit is False and callinfo.encodingStyle != 'encoded':
                raise ConfigException, 'operation(%s) is not rpc style' %name

    def setSection(self, section):
        """section -- this is the section the service is categorized in,
               if set STC will do a sanity check against the WSDL, etc.
        """
        self._section = section 

    def getSection(self):
        return self._section

    def getInputMessageInstance(self, operationName):
        """Returns an instance of the input message to send for this operation.
           Assuming there is only 1 service/wsdl, and 1 port/service.

           operationName -- WSDL port operation name
        """
        portAdapter = self._getPortAdapter()
        self.checkPort(portAdapter, operationName)
        operationList = portAdapter.getBinding().getPortType().getOperationList()
        for operationAdapter in operationList:
            if operationAdapter.getName() == operationName: break
        else:
            raise TestException, 'Missing operation (%s) in portType operations'  %operationName
        inputMsgName = '%sWrapper' %operationAdapter.getInput().getMessage().getName()
        if self._moduleDict.has_key(self._serviceModuleName):
            sm = self._moduleDict[self._serviceModuleName]
            if sm.__dict__.has_key(inputMsgName):
                inputMsgWrapper = sm.__dict__[inputMsgName]()
                return inputMsgWrapper
        raise TestException, 'port(%s) does not define operation %s' %(portAdapter.getName(), operationName)

    def RPC(self, operationName, request):
        """RPC serializes request, and returns response.

           operationName -- WSDL port operation name
        """
        callMethod = getattr(self._port, operationName)
        if callMethod:
            callMethod(request)
        raise TestException, 'Port instance is missing method %s' %operationName 


class ServiceTestSuite(unittest.TestSuite):
    """A test suite is a composite test consisting of a number of TestCases.

    For use, create an instance of TestSuite, then add test case instances.
    When all tests have been added, the suite can be passed to a test
    runner, such as TextTestRunner. It will run the individual test cases
    in the order in which they were added, aggregating the results. When
    subclassing, do not forget to call the base class constructor.
    """
    def __init__(self, tests=()):
        unittest.TestSuite.__init__(self, tests)
        self._section = None

    def setSection(self, section):
        self._section = section

    def addTest(self, test):
        if isinstance(test, ServiceTestCase):
            test.setSection(self._section)
        unittest.TestSuite.addTest(self, test)

