#!/usr/bin/env python
############################################################################
# Joshua R. Boverhof, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################

import os, sys, unittest, urlparse, signal, time, warnings
from ConfigParser import ConfigParser, NoSectionError, NoOptionError
from ZSI.wstools import WSDLTools
from ZSI.wstools.Namespaces import WSA200408, WSA200403, WSA200303
from ZSI.wstools.logging import setBasicLoggerDEBUG
from ZSI.wstools.TimeoutSocket import TimeoutError
from ZSI.generate.wsdl2python import WriteServiceModule
from ZSI.generate.wsdl2dispatch import ServiceModuleWriter, WSAServiceModuleWriter
import StringIO, copy, getopt

# set up pyclass metaclass for complexTypes
from ZSI.generate.containers import TypecodeContainerBase, TypesHeaderContainer
TypecodeContainerBase.metaclass = 'pyclass_type'
TypesHeaderContainer.imports.append(\
        'from ZSI.generate.pyclass import pyclass_type'
        )


sys.path.append('%s/%s' %(os.getcwd(), 'stubs'))
print sys.path[-1]

"""Global Variables:
    CONFIG_FILE -- configuration file 
    CONFIG_PARSER -- ConfigParser instance
    DOCUMENT -- test section variable, specifying document style.
    LITERAL -- test section variable, specifying literal encodings.
    BROKE -- test section variable, specifying broken test.
    TESTS -- test section variable, whitespace separated list of modules.
    SECTION_CONFIGURATION -- configuration section, turn on/off debuggging.
    TRACEFILE -- file class instance.
    TOPDIR -- current working directory
    MODULEDIR  -- stubs directory 
    PORT -- port of local container
    HOST -- address of local container
    SECTION_SERVERS -- services to be tested, values are paths to executables.
"""
CONFIG_FILE = 'config.txt'
CONFIG_PARSER = ConfigParser()
DOCUMENT = 'document'
LITERAL = 'literal'
BROKE = 'broke'
TESTS = 'tests'
SECTION_CONFIGURATION = 'configuration'
TRACEFILE = sys.stdout
TOPDIR = os.getcwd()
MODULEDIR = TOPDIR + '/stubs'
PORT = 'port'
HOST = 'host'
SECTION_SERVERS = 'servers'

CONFIG_PARSER.read(CONFIG_FILE)
if CONFIG_PARSER.getboolean(SECTION_CONFIGURATION, 'debug'):
    setBasicLoggerDEBUG()

ENVIRON = copy.copy(os.environ)
ENVIRON['PYTHONPATH'] = ENVIRON.get('PYTHONPATH', '') + ':' + MODULEDIR


def WriteServiceStubModule(wsdl):
    '''Create/Write Service Skeleton module.  If WS-Addressing schema is present 
    assume this is a WS-Address enabled service.
    '''
    if len(filter(lambda addr: wsdl.types.has_key(addr), (WSA200408.ADDRESS, WSA200403.ADDRESS, WSA200303.ADDRESS))) > 0:
        ss = WSAServiceModuleWriter
    else:
        ss = ServiceModuleWriter()
    ss.fromWSDL(wsdl)
    module_name = ss.getServiceModuleName()
    fd = open(module_name + '.py', 'w+')
    ss.write(fd)
    fd.close()
    return module_name


def SpawnContainer(ex_name):
    '''module_name must be executable, and set up ServiceContainer
    to test against.
    ex -- executable name
    '''
    port = CONFIG_PARSER.get(SECTION_CONFIGURATION, PORT)
    processID = os.spawnle(os.P_NOWAIT, ex_name, ex_name, port, ENVIRON)
    time.sleep(1)
    return processID


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
           _ports -- soap ports (must be same binding), proxy rpc instance, to run tests on.
           _portName -- The name of the port to get using _getPort
           _importTypeModule -- boolean indicating whether to import the types file 
           _typeModuleName -- key to the generated type module
           _serviceModuleName -- key to the generated service module
           _section -- if set, do a runtime check that test is correctly indexed.
           _wsm -- WriteServiceModule instance
        """
        self._moduleDict = {}
        self._ports = None
        self._portName = None
        self._importTypeModule = True
        self._typeModuleName = None
        self._serviceModuleName = None
        self._wsm = None
        self._section = None
        self._processID = None
        unittest.TestCase.__init__(self, methodName)

    def setUp(self):
        """Generate types and services modules if no record of them
           in the moduleDict variable.
        """
        
        if not self.url_section or not self.name:
            raise TestException, 'section(%s) or name(%s) not defined' %(self.url_section,self.name)
        if self._isSetModules():
            return
        if not CONFIG_PARSER.has_section(self.url_section):
            raise TestException, 'No such section(%s) in configuration file(%s)' \
                %(self.url_section, CONFIG_FILE)

        try:
            os.mkdir(MODULEDIR)
        except OSError, ex:
            pass

        os.chdir(MODULEDIR)
        if MODULEDIR not in sys.path:
            sys.path.append(MODULEDIR)

        reader = WSDLTools.WSDLReader()
        url = CONFIG_PARSER.get(self.url_section, self.name)

        try:
            wsdl = reader.loadFromURL(url)
        except TimeoutError:
            # SKIP 
            self.fail('socket timeout retrieving WSDL: %s' %url)
            os.chdir(TOPDIR)
        except:
            os.chdir(TOPDIR)
            raise
           
        try:
            self._wsm = WriteServiceModule(wsdl)
            fd = open('%s.py' %self._wsm.getTypesModuleName(), 'w+')
            self._wsm.writeTypes(fd)
            fd.close()
            fd = open('%s.py' %self._wsm.getClientModuleName(), 'w+')
            self._wsm.writeClient(fd)
            fd.close()
            self._setModuleNames(self._importTypeModule)
            module_name = WriteServiceStubModule(wsdl)
        finally:
            os.chdir(TOPDIR)

        locator = self._getLocator()
        self._ports = []
        if CONFIG_PARSER.getboolean(SECTION_CONFIGURATION, 'net'):
            self._ports.append(self._getPort(locator))

        if CONFIG_PARSER.getboolean(SECTION_CONFIGURATION, 'local'):
            netloc = '%s:%d' %(CONFIG_PARSER.get(SECTION_CONFIGURATION, HOST),
                CONFIG_PARSER.getint(SECTION_CONFIGURATION, PORT))
            try:
                ex_path = CONFIG_PARSER.get(SECTION_SERVERS, self.name)
            except (NoSectionError, NoOptionError), ex:
                warnings.warn('skipping local test for %s' %self.name)
            else:
                self._ports.append(self._getPort(locator, netloc=netloc))
                self._processID = SpawnContainer(TOPDIR + '/' + ex_path)

    def tearDown(self):
        """
        This must be deleted because it has reference to
        a namespace hash object which keeps its dictionary in
        a class variable.If we run multiple ServiceTestSuites then
        namespaces in the first prior ServiceTestSuite will remain
        in the hash, and the code generator will import them in the
        We need a fresh namespace hash each time a unittest is run
        """
        del self._wsm
        if self._processID is not None:
            os.kill(self._processID, signal.SIGKILL)
        
    def _getPortOptions(self, methodName, locator, netloc=None):
        kw = {}
        if CONFIG_PARSER.getboolean(SECTION_CONFIGURATION, 'tracefile'):
            kw['tracefile'] = TRACEFILE

        if netloc is not None:
            default_url = getattr(locator, methodName + 'Address')()
            scheme, netloc_old, url, params, query, fragment = urlparse.urlparse(default_url)
            kw['url'] = urlparse.urlunparse((scheme, netloc, url, params, query, fragment))

        return kw

    def _getLocator(self):
        """Get the Locator name
           **Only expecting 1 service/WSDL, and 1 port/service.
           wsm -- WriteServiceModule instance
        """
        if len(self._wsm.services) != 1:
            raise TestException, 'only supporting WSDL with one service information item'
        locatorName = self._wsm.services[0].locator.getLocatorName()
        if self._moduleDict.has_key(self._serviceModuleName):
            sm = self._moduleDict[self._serviceModuleName]
            if sm.__dict__.has_key(locatorName):
                return sm.__dict__[locatorName]()
            raise TestException, 'No Locator class (%s), missing SOAP location binding?' %locatorName
        raise TestException, 'missing service module, possibly no WSDL service item?'

    def _getPort(self, locator, netloc=None):
        """Returns a rpc proxy port instance.
           **Only expecting 1 service/WSDL, and 1 port/service.

           locator -- Locator instance
        """
        if len(self._wsm.services) != 1:
            raise TestException, 'only supporting WSDL with one service information item'
        methodNames = self._wsm.services[0].locator.getPortMethods()
        if len(methodNames) == 0: 
            raise TestException, 'No port defined for service.'
        elif len(methodNames) > 1:
            raise TestException, 'Not handling multiple ports.'
        callMethod = getattr(locator, methodNames[0])
        return callMethod(**self._getPortOptions(methodNames[0], locator, netloc))

    def _isSetModules(self):
        """Are the types/service modules already loaded?
        """
        if self._serviceModuleName: 
            return True
        return False

    def _setModuleNames(self, importTypes=True):
        """set service and types modules key names, and import them.

           Some of the no schema tests do generate a types file
        """
        self._typeModuleName = self._wsm.getTypesModuleName()
        self._serviceModuleName = self._wsm.getClientModuleName()
        if importTypes:
            moduleTuple = (self._typeModuleName, self._serviceModuleName)
        else:
            moduleTuple = (self._serviceModuleName,)

        for name in moduleTuple:
            exec('import %s' %name)
            self._moduleDict[name] = eval(name)


    def checkSection(self):
        """Should the section be checked? If I know about it.
        """
        return type(self._section) is str

    def _checkPort(self, port, name):
        """Check if test is in correctly indexed in the configuration file, 
           port operation must conform to the bindings.  

           We check the style and use attributes from the soapOperation element.
           
           port -- WSDLTools.Port instance
           name -- WSDL port operation name
           port -- WSDLTools.Port instance
        """
        if self.checkSection() is False:
            return

        doc = CONFIG_PARSER.getboolean(self.getSection(), DOCUMENT)
        lit = CONFIG_PARSER.getboolean(self.getSection(), LITERAL)
        binding = port.getBinding()
        if binding.operations.has_key(name) is False:
            raise TestException, 'port(%s) binding(%s) has no operation(%s)'\
                %(port.name, port.type, name)

        soapbinding = binding.findBinding(WSDLTools.SoapBinding)
        if soapbinding is None:
            raise TestException, 'Missing soap:binding element'

        opbinding = binding.operations[name]
        if opbinding.input is None:
            raise TestException, 'wsdl:binding(%s) operation(%s) is missing input' \
                %(binding.name, name)
       
        msgrole = opbinding.input
        soap_op_binding = opbinding.findBinding(WSDLTools.SoapOperationBinding)
        style = soap_op_binding.style or soapbinding.style
        use = None
        body = msgrole.findBinding(WSDLTools.SoapBodyBinding)
        if body is None:
            raise TestException, 'Missing soap:body element'

        use = body.use
        style = soap_op_binding.style or soapbinding.style
        if doc and style != 'document':
            raise ConfigException, 'operation(%s) is not document style' %name
        elif not doc and style != 'rpc':
            raise ConfigException, 'operation(%s) is not rpc style' %name
        if lit is True and use != 'literal':
            raise ConfigException, 'operation(%s) is not literal encoding' %name
        if lit is False and use != 'encoded':
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
        service = self._wsm._wsdl.services[0]
        port = service.ports[0]
        try:
            self._checkPort(port, operationName)
        except TestException, ex:
            raise TestException('Service(%s)' %service.name, *ex.args)

        for operation in port.getBinding().getPortType().operations:
            if operation.name == operationName: 
                break
        else:
            raise TestException, 'Missing operation (%s) in portType operations'  %operationName

        inputMsgName = '%s' %operation.input.message[1]
        if self._moduleDict.has_key(self._serviceModuleName):
            sm = self._moduleDict[self._serviceModuleName]
            if sm.__dict__.has_key(inputMsgName):
                inputMsgWrapper = sm.__dict__[inputMsgName]()
                return inputMsgWrapper
            else:
                raise TestException, 'service missing input message (%s)' %(inputMsgName)

        raise TestException, 'port(%s) does not define operation %s' \
            %(port.name, operationName)

    def RPC(self, operationName, request):
        """RPC serializes request, and returns response.

           operationName -- WSDL port operation name
        """
        for port in self._ports:
            callMethod = getattr(port, operationName, None)
            if callMethod is not None:
                callMethod(request)
            else:
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
        if isinstance(test, ServiceTestSuite):
            test.setSection(self._section)
        unittest.TestSuite.addTest(self, test)

