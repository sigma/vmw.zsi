############################################################################
# David W. Robertson, LBNL
# See Copyright for copyright notice!
###########################################################################

import unittest
import sys, os, os.path
import getopt
import StringIO, copy, re
import unittest, ConfigParser
import inspect

from ZSI import wsdl2python
from ZSI.wstools.WSDLTools import WSDLReader
from ZSI import FaultException

from clientGenerator import ClientGenerator
from paramWrapper import ResultsToStr

"""
utils:
    This module contains a class that test instances sub-class, a class
    encapsulating comparisons against a test file, and a test program
    class allowing additional command-line arguments.
"""

class ServiceTestCase(unittest.TestCase):

    def getConfigOptions(self, configFile, configSection, serviceName):
        kw = {}
        cp = CaseSensitiveConfigParser()
        cp.read(configFile)
        serviceLoc = cp.get(configSection, serviceName)
        useTracefile = cp.get('configuration', 'tracefile') 
        if useTracefile == '1':
            kw['tracefile'] = sys.stdout
        try:
            snifferHost = setUp.get('configuration', 'host')
        except NameError:
            pass
        else:
            snifferPort = setUp.get('configuration', 'port')
            if not snifferPort:
                snifferPort = 80
            kw['host'] = snifferHost
            kw['port'] = snifferPort

        return kw, serviceLoc

    def setService(self, serviceLoc, serviceName, portTypeName, **kw):
        """Returns reference to higher-level interface module, generating
           the _services, _types, and _services_interface code if
           necessary, and a reference to a class containing proxy
           methods for the operations listed in the WSDL portType.
        """
           
        serviceModule = ClientGenerator().getModule(serviceName, serviceLoc,
                                                        'stubs')
        if not serviceModule:
            return None, None

        try:
            locator = serviceModule.__dict__[portTypeName + 'HLocator']
        except KeyError:
            print 'Test requires helper interface generation'
            return None, None

        portType = locator().getPortType(portTypeName, **kw)
        return serviceModule, portType

    def setUpWsdl(path):
        """Load a WSDL given a file path or a URL.
        """
        if path[:7] == 'http://':
            wsdl = WSDLReader().loadFromURL(path)
        else:
            wsdl = WSDLReader().loadFromFile(path)
        return wsdl


    def handleResponse(self, fun, request, diff=None):
        try:
            response = fun(request)
        except FaultException, msg:
            if self.checkException(FaultException, msg):
                raise
        else:
            if not diff:
                print ResultsToStr(response)
            else:
                TestDiff(self).failUnlessEqual(ResultsToStr(response))



    def checkException(self, exc, msg):
        """Determines whether an exception occurred due to a
           timeout, in which case the result of a test is not
           treated as a failure.
        """
 
        if (msg.str.startswith('Connection timed out') or
            msg.str.find('timeout')):
            print '\n', msg
            print '\n'
            sys.stdout.flush()
            return False
        else:
            return True
        


def handleExtraArgs(argv):
    deleteFile = False
    options, args = getopt.getopt(argv, 'hHdv')
    for opt, value in options:
        if opt == '-d':
            deleteFile = True
    return deleteFile


class CaseSensitiveConfigParser(ConfigParser.ConfigParser):

    def __init__(self):
        ConfigParser.ConfigParser.__init__(self)

    def optionxform(self, optionstr):
        """Overriding ConfigParser method allows configuration option
           to contain both lower and upper case."""
        return optionstr




class TestDiff:
    """TestDiff encapsulates comparing a string or StringIO object
       against text in a test file.  Test files are located in a
       subdirectory of the current directory, named diffs if a name
       isn't provided.  If the sub-directory doesn't exist, it will
       be created.  If a single test file is to be generated, the file
       name is passed in.  If not, another sub-directory is created
       below the diffs directory, in which a file is created for each
       test.

       The calling unittest.TestCase instance is passed
       in on object creation.  Optional compiled regular expressions
       can also be passed in, which are used to ignore strings
       that one knows in advance will be different, for example
       id="<hex digits>" .

       The initial running of the test will create the test
       files.  When the tests are run again, the new output
       is compared against the old, line by line.  To generate
       a new test file, remove the old one from the sub-directory.
       The tests also allow this to be done automatically if the
       -d option is passed in on the command-line.
    """

    def __init__(self, testInst, testFilePath='diffs', singleFileName='',
                *ignoreList):
        self.diffsFile = None
        self.testInst = testInst
        self.origStrFile = None
        self.expectedFailures = copy.copy(ignoreList)

        if not os.path.exists(testFilePath):
            os.mkdir(testFilePath)

        if not singleFileName:
            #  if potentially multiple tests will be performed by
            #  a test module, create a subdirectory for them.
            testFilePath = testFilePath + os.sep + testInst.__class__.__name__
            if not os.path.exists(testFilePath):
                os.mkdir(testFilePath)

                # get name of test method, and name the diffs file after
                # it
            f = inspect.currentframe()
            fullName = testFilePath + os.sep + \
                       inspect.getouterframes(f)[2][3] + '.diffs'
        else:
            fullName = testFilePath + os.sep + singleFileName

        deleteFile = handleExtraArgs(sys.argv[1:])
        if deleteFile:
            try:
                os.remove(fullName)
            except OSError:
                print fullName

        try:
            self.diffsFile = open(fullName, "r")
            self.origStrFile = StringIO.StringIO(self.diffsFile.read())
        except IOError:
            try:
                self.diffsFile = open(fullName, "w")
            except IOError:
                print "exception"


    def failUnlessEqual(self, buffer):
        """failUnlessEqual takes either a string or a StringIO
           instance as input, and compares it against the original
           output from the test file.  
        """
            # if not already a string IO 
        if not isinstance(buffer, StringIO.StringIO):
            testStrFile = StringIO.StringIO(buffer)
        else:
            testStrFile = buffer
            testStrFile.seek(0)

        hasContent = False
        if self.diffsFile.mode == "r":
            for testLine in testStrFile:
                origLine = self.origStrFile.readline() 
                if not origLine:
                    break
                else:
                    hasContent = True

                    # take out expected failure strings before
                    # comparing original against new output
                for cexpr in self.expectedFailures:
                    origLine = cexpr.sub('', origLine)
                    testLine = cexpr.sub('', testLine)

                if origLine != testLine:
                    self.testInst.failUnlessEqual(origLine, testLine)
            return

        if (self.diffsFile.mode == "w") or not hasContent:
                # write new test file
            for line in testStrFile:
                self.diffsFile.write(line)

        self.diffsFile.close()


class TestProgram(unittest.TestProgram):
    """A command-line program that runs a set of tests.  Overrides
       parseArgs to allow additional command-line arguments.
    """
    USAGE = """\
Usage: %(progName)s [options] [test] [...]

Options:
  -h, --help       Show this message
  -d               Delete diffs file before running

Examples:
  %(progName)s                               - run default set of tests
  %(progName)s MyTestSuite                   - run suite 'MyTestSuite'
  %(progName)s MyTestCase.testSomething      - run MyTestCase.testSomething
  %(progName)s MyTestCase                    - run all 'test*' test methods
                                               in MyTestCase
"""
    def __init__(self, module='__main__', defaultTest=None,
                 argv=None, testRunner=None, testLoader=None):
        if not testLoader:
            testLoader = unittest.defaultTestLoader
        unittest.TestProgram.__init__(self, module, defaultTest, argv,
                                            testRunner, testLoader)

    def parseArgs(self, argv):
        import getopt
        try:
                # -d is handled prior to this call, but is included
                # to avoid an error message.  -v is ignored.
            options, args = getopt.getopt(argv[1:], 'hHdv',
                                          ['help'])
            for opt, value in options:
                if opt in ('-h','-H','--help'):
                    self.usageExit()
            self.verbosity = 2
            if len(args) == 0 and self.defaultTest is None:
                self.test = self.testLoader.loadTestsFromModule(self.module)
                return
            if len(args) > 0:
                self.testNames = args
            else:
                self.testNames = (self.defaultTest,)
            self.createTests()
        except getopt.error, msg:
            self.usageExit(msg)

    def runTests(self):
        if self.testRunner is None:
            self.testRunner = unittest.TextTestRunner(verbosity=self.verbosity)
        result = self.testRunner.run(self.test)
            # may want global cleanup; sys.exit removed here
