#!/usr/bin/env python
############################################################################
# Joshua R. Boverhof, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import os, sys, unittest, time
from ServiceTest import ServiceTestCase, ServiceTestSuite
from ZSI import FaultException
from ZSI.TC import _get_global_element_declaration as GED
from ZSI.writer import SoapWriter
from ZSI.parse import ParsedSoap

"""
Unittest for Bug Report 
[ ] 

WSDL:  
"""

CONFIG_FILE = 'config.txt'
sys.path.append('%s/%s' %(os.getcwd(), 'stubs'))

class AttributeTest(unittest.TestCase):
    name = "test_Attributes"
    done = False

    def setUp(self):
        if AttributeTest.done: return
        AttributeTest.done = True
        wsdl = os.path.abspath('test_Attributes.xsd').strip()
        fin,fout = os.popen4('cd stubs; wsdl2py.py -x -b -f %s' %wsdl)
        # TODO: wait for wsdl2py.py to finish.
        for i in fout: print i
        import test_Attributes_xsd_services_types
 
    def tearDown(self):
        pass

    def test_attribute1(self):
        """
        """
        myDouble = 4.5
        myInt = 9
        myFloat = 3.0001
        myDecimal = 8.999
        myGDateTime = time.gmtime()
        myAnyURI = "urn:whatever"
        myQName = ("urn:test", "qbert")
        myString = "whatever"
        myHexBinary = hex(888)

        pyobj = GED("urn:example", "Test1").pyclass()
        # Test serialize/parse
        pyobj.set_attribute_myDecimal(myDecimal)
        pyobj.set_attribute_myDouble(myDouble)
        pyobj.set_attribute_myFloat(myFloat)
        pyobj.set_attribute_myInt(myInt)
        pyobj.set_attribute_myDateTime(myGDateTime)

        pyobj.set_attribute_myGDay(myGDateTime)
        pyobj.set_attribute_myGMonth(myGDateTime)
        pyobj.set_attribute_myGYear(myGDateTime)
        pyobj.set_attribute_myGYearMonth(myGDateTime)
        pyobj.set_attribute_myDate(myGDateTime)
        pyobj.set_attribute_myTime(myGDateTime)

        pyobj.set_attribute_myAnyURI(myAnyURI)
        pyobj.set_attribute_myString(myString)
        pyobj.set_attribute_myHexBinary(myHexBinary)
        pyobj.set_attribute_myDuration(myGDateTime)

        # Problems parsings 
        pyobj.set_attribute_myQName(myQName)
        pyobj.set_attribute_myGMonthDay(myGDateTime)


        #TODO:
        #pyobj.set_attribute_myBase64Binary("")
        #pyobj.set_attribute_myNOTATION("NOT")

        sw = SoapWriter()
        sw.serialize(pyobj)
        soap = str(sw)
 
        print soap
        ps = ParsedSoap(soap)
        pyobj2 = ps.Parse(pyobj.typecode)

        test = pyobj2.get_attribute_myInt()
        self.failUnlessEqual(myInt, test)

        test = pyobj2.get_attribute_myDouble()
        self.failUnlessEqual(myDouble, test)

        test = pyobj2.get_attribute_myFloat()
        self.failUnlessEqual(myFloat, test)

        test = pyobj2.get_attribute_myDecimal()
        self.failUnlessEqual(myDecimal, test)

        test = pyobj2.get_attribute_myAnyURI()
        self.failUnlessEqual(myAnyURI, test)

        test = pyobj2.get_attribute_myQName()
        self.failUnlessEqual(myQName, test)

        test = pyobj2.get_attribute_myString()
        self.failUnlessEqual(myString, test)

        test = pyobj2.get_attribute_myHexBinary()
        self.failUnlessEqual(myHexBinary, test)

        # DateTime stuff
        test = pyobj2.get_attribute_myDateTime()
        self.failUnlessEqual(myGDateTime[:-3], test[:-3])

        test = pyobj2.get_attribute_myDate()
        self.failUnlessEqual(myGDateTime[:3], test[:3])

        test = pyobj2.get_attribute_myTime()
        self.failUnlessEqual(myGDateTime[4:5], test[4:5])

        test = pyobj.get_attribute_myDuration()
        self.failUnlessEqual(myGDateTime, test)

        # Bug [ 1453421 ] Incorrect format for type gDay
        test = pyobj2.get_attribute_myGDay()
        self.failUnlessEqual(myGDateTime[2], test[2])

        test = pyobj2.get_attribute_myGMonth()
        self.failUnlessEqual(myGDateTime[1], test[1])

        test = pyobj2.get_attribute_myGYear()
        self.failUnlessEqual(myGDateTime[0], test[0])

        test = pyobj2.get_attribute_myGYearMonth()
        self.failUnlessEqual(myGDateTime[:2], test[:2])

        # hmm? negated?
        #test = pyobj2.get_attribute_myGMonthDay()
        #self.failUnlessEqual(myGDateTime[1:3], test[1:3])

    def test_empty_attribute(self):
        # [ 1452752 ] attribute with empty value doesn't appear in parsed object
        myString = ""
        pyobj = GED("urn:example", "Test1").pyclass()
        pyobj.set_attribute_myString(myString)

        sw = SoapWriter()
        sw.serialize(pyobj)
        soap = str(sw)
 
        print soap
        ps = ParsedSoap(soap)
        pyobj2 = ps.Parse(pyobj.typecode)

        test = pyobj2.get_attribute_myString() 
        self.failUnlessEqual(myString, str(test))


def makeTestSuite():
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(AttributeTest, "test_", suiteClass=ServiceTestSuite))
    return suite


if __name__ == "__main__" :
    unittest.TestProgram(defaultTest="makeTestSuite")

