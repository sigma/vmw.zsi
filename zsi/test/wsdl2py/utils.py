############################################################################
# David W. Robertson, LBNL
# See Copyright for copyright notice!
###########################################################################

from __future__ import generators

import sys, os, os.path, pickle
import shutil, getopt
import StringIO, copy, re
import unittest, ConfigParser
from ZSI import wsdl2python
from pyGridWare.GWSDLTools import GWSDLReader

"""
utils:
    This module contains utility functions for use by test case modules, a
    class facilitating the use of ConfigParser with multiple test cases, a
    class encapsulating comparisons against a test file, and a test loader
    class with a different loading strategy than the default
    unittest.TestLoader.
"""

thisFileName = sys.modules[__name__].__file__

class ConfigHandler(ConfigParser.ConfigParser):

    def __init__(self, name="config.txt"):
        ConfigParser.ConfigParser.__init__(self)
            # first, look for one in this directory
            # Done this way because it turns out read fails silently
        self.read(name)
        if not self.sections():
            print '%s not found\n' % name
            sys.exit(0)

    
    def getConfigNames(self, sections, numMethods, valueFunc=None):
        """A generator which returns one value from a given config
           file section at a time.  It also optionally calls a
           passed-function for that value, and yields the result as well.
        """

        result = None
        for section in sections:
            for name, value in self.items(section):
                for i in range(0, numMethods):
                    yield value	# indicate which test in all cases
                    if i == 0:
                        result = None
                        if valueFunc:
                            try:
                                result = valueFunc(value)
                            except KeyboardInterrupt:
                                sys.exit(-1)   # for now
                            except:		# don't care, test will be skipped
                                pass
                    if valueFunc:
                        yield result


    def length(self, sections):
        """Determines the total number of items in all the
           chosen sections from a config file.
        """
        total = 0
        for section in sections:
            total += len(self.options(section))
        return total 


def handleExtraArgs(argv):
    deleteFile = False
    options, args = getopt.getopt(argv, 'hHdv')
    for opt, value in options:
        if opt == '-d':
            deleteFile = True
    return deleteFile


def setUpWsdl(path):
    """Load a WSDL given a file path or a URL.
    """
    if path[:7] == 'http://':
        wsdl = GWSDLReader().loadFromURL(path)
    else:
        wsdl = GWSDLReader().loadFromFile(path)
    return wsdl


class ClientGenerator:

    def generateCode(self, section, serviceName, subdirPath='.',
                     schemaOnly=False, explicitPath=None):
        subdirPath = os.path.dirname(thisFileName) + os.sep + subdirPath
        if not os.path.exists(subdirPath):
            os.mkdir(subdirPath)
        if not os.path.exists(subdirPath + os.sep + '__init__.py'):
            try:
                shutil.copy('test.init.py', subdirPath + os.sep + '__init__.py')
            except:
                shutil.copy(os.path.dirname(thisFileName) + os.sep + 'test.init.py', subdirPath + os.sep + '__init__.py')
        if section:
            ch = ConfigHandler()
            path = ch.get(section, serviceName)
        else:
            path = explicitPath
        wsdl = setUpWsdl(path)
        codegen = wsdl2python.WriteServiceModule(wsdl)
        f_types, f_services = codegen.get_module_names()
        hasSchema = len(codegen._wa.getSchemaDict())

        if hasSchema:
            fd = open(subdirPath + os.sep + f_types + '.py', 'w+')
            codegen.write_service_types(f_types, fd)
            fd.close()

        if schemaOnly:
            return

        fd = open(subdirPath + os.sep + f_services + '.py', 'w+')
        codegen.write_services(f_types, f_services, fd, hasSchema)
        fd.close()


class TestDiff:
    """TestDiff encapsulates comparing a string or StringIO object
       against text in a test file.  Test files are expected to
       be located in a subdirectory of the current directory,
       named data if a name isn't provided.  If the sub-directory
       doesn't exist, it will be created

       If used in a test case, this should be instantiated in setUp and
       closed in tearDown.  The calling unittest.TestCase instance is passed
       in on object creation.  Optional compiled regular expressions
       can also be passed in, which are used to ignore strings
       that one knows in advance will be different, for example
       id="<hex digits>" .

       The initial running of the test will create the test
       files.  When the tests are run again, the new output
       is compared against the old, line by line.  To generate
       a new test file, remove the old one from the sub-directory.
    """

    def __init__(self, testInst, subDir='data', *ignoreList):
        self.SUBDIR = subDir
        self.dataFile = None
        self.testInst = testInst
        self.origStrFile = None
            # used to divide separate test blocks within the same
            # test file.
        self.divider = "#" + ">" * 75 + "\n"
        self.expectedFailures = copy.copy(ignoreList)
        self.testFilePath = self.SUBDIR + os.sep
        if not os.path.exists(self.testFilePath):
            os.mkdir(self.testFilePath)

        

    def setDiffFile(self, fname):
        """setDiffFile attempts to open the test file with the
           given name, and read it into a StringIO instance.
           If the file does not exist, it opens the file for
           writing.
        """
        filename = fname
        if self.dataFile and not self.dataFile.closed:
            self.dataFile.close()
        try:
            self.dataFile = open(self.testFilePath + filename, "r")
            self.origStrFile = StringIO.StringIO(self.dataFile.read())
        except IOError:
            try:
                self.dataFile = open(self.testFilePath + filename, "w")
            except IOError:
                print "exception"

    def deleteFile(self, fname):
        try:
            os.remove(self.testFilePath + fname)
        except OSError:
            print self.testFilePath + fname


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
        if self.dataFile.mode == "r":
            for testLine in testStrFile:
                origLine = self.origStrFile.readline() 
                    # skip divider
                if origLine == self.divider:
                    origLine = self.origStrFile.readline() 

                    # take out expected failure strings before
                    # comparing original against new output
                for cexpr in self.expectedFailures:
                    origLine = cexpr.sub('', origLine)
                    testLine = cexpr.sub('', testLine)
                if origLine != testLine:    # fails
                    # advance test file to next test
                    line = origLine
                    while line and line != self.divider:
                        line = self.origStrFile.readline() 
                    self.testInst.failUnlessEqual(origLine, testLine)

        else:       # write new test file
            for line in testStrFile:
                self.dataFile.write(line)
            self.dataFile.write(self.divider)


    def close(self):
        """Closes handle to original test file.
        """
        if self.dataFile and not self.dataFile.closed:
            self.dataFile.close()


    def getSubdirName(self):
        return self.SUBDIR


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


class MatchTestLoader(unittest.TestLoader):
    """Overrides unittest.TestLoader.loadTestsFromNames to provide a
       simpler and less verbose way to select a subset of tests to run.
       If all tests will always be run, use unittest.TestLoader instead. 

       If a top-level test invokes test cases in other modules,
       MatchTestLoader should be created with topLevel set to True
       to get the correct results.  For example,

       def main():
           loader = utils.MatchTestLoader(True, None, "makeTestSuite")
           unittest.main(defaultTest="makeTestSuite", testLoader=loader)

       The defaultTest argument in the constructor indicates the test to run
       if no additional arguments beyond the test script name are provided.
    """

    def __init__(self, topLevel, configName, defaultTest):
        unittest.TestLoader.__init__(self)
        self.testMethodPrefix = "test"
        self.defaultTest = defaultTest
        self.topLevel = topLevel
        if configName:
	    self.config = ConfigHandler(configName)
        self.sections = []
	self.nameGenerator = None
    

    def setUpArgs(self):
        """Sets up the use of arguments from the command-line to select
           tests to run.  There can be multiple names, both in full or as
           a substring, on the command-line.
        """
        sectionList = self.config.sections()
        self.testArgs = []
        argv = []
           # ignore section names in determining what to
           # load (sys.argv can be passed into setSection,
           # where any section names are extracted)
        for name in sys.argv:
            if name not in sectionList:
                argv.append(name)
        if not self.topLevel or (len(argv) != 1):
            for arg in argv[1:]:
                if arg.find("-") != 0:
                    self.testArgs.append(arg)
            # has the effect of loading all tests
        if not self.testArgs:
            self.testArgs = [None]


    def loadTestsFromNames(self, unused, module=None):
        """Hard-wires using the default test.  It ignores the names
           passed into it from unittest.TestProgram, because the
           default loader would fail on substrings or section names.
        """

        suites = unittest.TestLoader.loadTestsFromNames(self,
                                  (self.defaultTest,), module)
        return suites



    def setSection(self, args):
        """Sets section(s) of config file to read.
        """
        sectionList = self.config.sections()
        if ((type(args) is list) or
             (type(args) is tuple)):
            for arg in args:
                if arg in sectionList:
                    self.sections.append(arg)
            if self.sections:
                return True
        elif type(args) is str:
            if args in sectionList:
                self.sections.append(args)
                return True
        return False



    def loadTestsFromConfig(self, testCaseClass, valueFunc=None):
        """Loads n number of instances of testCaseClass, where
           n is the number of items in the config file section(s).
           getConfigNames is a generator which is used to parcel
           out the values in the section(s) to the testCaseClass
           instances.
        """

        self.setUpArgs()
        numTestCases = self.getTestCaseNumber(testCaseClass)
        self.nameGenerator = self.config.getConfigNames(self.sections,
                                     numTestCases, valueFunc)
        configLen = self.config.length(self.sections)
        suite = unittest.TestSuite()
        for i in range(0, configLen):
            suite.addTest(self.loadTestsFromTestCase(testCaseClass))
        return suite


    def getTestCaseNumber(self, testCaseClass):
        """Looks for any test methods whose name contains testStr, checking
           if a test method has already been added.  If there is not a match,
           it checks for an exact match with the test case name, and
           returns the number of test cases.
        """
        methods = self.getTestCaseNames(testCaseClass)
        prevAdded = []
        counter = 0
	for testStr in self.testArgs:
            if testStr:
                for m in methods:
                    if m.find(testStr) >= 0 and m not in prevAdded:
                        counter = counter + 1
                        prevAdded.append(m)
                if counter:
                    return counter
            if (not testStr) or (testCaseClass.__name__ == testStr):
                for m in methods:
                    counter = counter + 1
                    prevAdded.append(m)
#        print "found %d cases" % counter
        return counter


    def loadTestsFromTestCase(self, testCaseClass):
        """looks for any test methods whose name contains testStr, checking
           if a test method has already been added.  If there is not a match,
           it checks for an exact match with the test case name, and loads
           all methods if so.
        """
        methods = self.getTestCaseNames(testCaseClass)
        prevAdded = []
        suites = unittest.TestSuite()
	for testStr in self.testArgs:
#            print testStr
            if testStr:
                for m in methods:
                    if m.find(testStr) >= 0 and m not in prevAdded:
                        suites.addTest(testCaseClass(m))
                        prevAdded.append(m)
        if suites.countTestCases():
            return suites
        for testStr in self.testArgs:
            if (not testStr) or (testCaseClass.__name__ == testStr):
                for m in methods:
                    suites.addTest(testCaseClass(m))
                    prevAdded.append(m)
                if suites.countTestCases():
                    return suites
        return suites
