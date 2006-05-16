#!/usr/bin/env python
############################################################################
# Joshua R. Boverhof, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import os, sys, unittest
from ServiceTest import main, ServiceTestCase, ServiceTestSuite
from ZSI import FaultException
from ZSI.writer import SoapWriter
from ZSI.parse import ParsedSoap
from ZSI.TC import _get_type_definition as GTD
from ZSI.TC import _get_global_element_declaration as GED

"""
Unittest 

WSDL:  derivedTypes.
"""

# General targets
def dispatch():
    """Run all dispatch tests"""
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(DTTestCase, 'test_dispatch'))
    return suite

def local():
    """Run all local tests"""
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(DTTestCase, 'test_local'))
    return suite

def net():
    """Run all network tests"""
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(DTTestCase, 'test_net'))
    return suite
    
def all():
    """Run all tests"""
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(DTTestCase, 'test_'))
    return suite


class DTTestCase(ServiceTestCase):
    name = "test_DerivedTypes"
    client_file_name = None
    types_file_name  = "test_DerivedTypes_xsd_services_types.py"
    server_file_name = None

    def __init__(self, methodName):
        ServiceTestCase.__init__(self, methodName)
        self.wsdl2py_args.append('-x')
        self.wsdl2py_args.append('-b')

    def test_local_ged_substitution(self):
        """This test is designed to fail, trying to dump
        a GED in via type substitution.
        """
        self.types_module
        pyobj = GED('urn:test', 'test').pyclass()
        
        # use GED of a derived type
        pyobj.Actor = sub = GED('urn:test', 'IfElseActor').pyclass()
        sub.Gui = 'foo'
        sub.Parameter = 'bar'
        
        sw = SoapWriter()
        self.failUnlessRaises(TypeError, sw.serialize, pyobj)
        
        
    def test_local_type_substitution(self):
        """Parse known instance, serialize an equivalent, Parse it back. """
        klass = 'myclass'
        name = 'whatever'
        self.types_module
        pyobj = GED('urn:test', 'test').pyclass()

        # [ 1489129 ] Unexpected subsitution error message
        #  try to parse before type ever initialized
        ps = ParsedSoap(MSG)
        pyobj0 = ps.Parse(pyobj.typecode)
        sub0 = pyobj0.Actor
        self.failUnless(sub0.get_attribute_class() == klass, 'bad attribute class')
        self.failUnless(sub0.get_attribute_name() == name, 'bad attribute name')

        # [ 1489090 ] Derived type attributes don't populate the attr dictionary
        # 
        pyobj.Actor = sub1 = GTD('urn:test', 'IfElseActor')(None).pyclass()
        sub1.Gui = 'foo'
        sub1.Parameter = 'bar'
        sub1.set_attribute_class(klass)
        sub1.set_attribute_name(name)
        
        sw = SoapWriter()
        sw.serialize(pyobj)
        xml = str(sw)
        print xml        
        ps = ParsedSoap(xml)
        pyobj2 = ps.Parse(pyobj.typecode)
        sub2 = pyobj2.Actor

        self.failUnless(sub2.get_attribute_class() == klass, 'bad attribute class')
        self.failUnless(sub2.get_attribute_name() == name, 'bad attribute name')
                
        # check parsed out correct type
        self.failUnless(isinstance(sub2.typecode, sub1.typecode.__class__), 
            'local element actor "%s" must be an instance of "%s"'%
                (sub2.typecode, sub1.typecode.__class__))
        
        # check local element is derived from base
        base = GTD('urn:test', 'BaseActor')
        self.failUnless(isinstance(sub2.typecode, base), 
            'local element actor must be a derived type of "%s"'%
                base)
        

MSG = """<SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><SOAP-ENV:Header></SOAP-ENV:Header><SOAP-ENV:Body xmlns:ns1="urn:test"><ns1:test><actor class="myclass" name="whatever" xsi:type="ns1:IfElseActor"><gui xsi:type="xsd:string">foo</gui><parameter xsi:type="xsd:string">bar</parameter></actor></ns1:test></SOAP-ENV:Body></SOAP-ENV:Envelope>"""


if __name__ == "__main__" :
    main()

