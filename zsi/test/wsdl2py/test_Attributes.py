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
        pyobj = GED("urn:example", "Test1").pyclass()
        pyobj.set_attribute_myAnyURI("urn:whatever")
        #pyobj.set_attribute_myBase64Binary("")
        pyobj.set_attribute_myDate(time.time())
        pyobj.set_attribute_myDateTime(time.time())
        pyobj.set_attribute_myDecimal(8.999)
        pyobj.set_attribute_myDouble(4.5)
        pyobj.set_attribute_myFloat(3.0001)
        pyobj.set_attribute_myGDay(time.time())
        pyobj.set_attribute_myGMonthDay(time.time())
        pyobj.set_attribute_myGYear(time.time())
        pyobj.set_attribute_myGYearMonth(time.time())
        pyobj.set_attribute_myHexBinary(hex(888))
        pyobj.set_attribute_myInt(9)
        pyobj.set_attribute_myQName(("urn:test", "qbert"))
        pyobj.set_attribute_myString("whatever")
        pyobj.set_attribute_myTime(time.time())

        #BROKE 
        #pyobj.set_attribute_myNOTATION("NOT")
        #pyobj.set_attribute_myGMonth(time.time())
        #pyobj.set_attribute_myDuration("DUR")

        sw = SoapWriter()
        sw.serialize(pyobj)
        soap = str(sw)
 
        print soap
        ps = ParsedSoap(soap)
        pyobj2 = ps.Parse(pyobj.typecode)
        for get in ['get_attribute_myInt','get_attribute_myDouble',
            'get_attribute_myFloat',]:
            #x = getattr(pyobj, get)()
            y = getattr(pyobj2, get)()
            #self.failUnlessEqual(x, y)
            print y


def makeTestSuite():
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(AttributeTest, "test_", suiteClass=ServiceTestSuite))
    return suite


if __name__ == "__main__" :
    unittest.TestProgram(defaultTest="makeTestSuite")

