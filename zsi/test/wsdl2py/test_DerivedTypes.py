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
        self.types_module
        pyobj = GED('urn:test', 'test').pyclass()
        # derived type
        pyobj.Actor = sub = GTD('urn:test', 'IfElseActor')(None).pyclass()
        
        sub.Gui = 'foo'
        sub.Parameter = 'bar'
        
        sw = SoapWriter()
        sw.serialize(pyobj)
        xml = str(sw)
        
        ps = ParsedSoap(xml)
        pyobj2 = ps.Parse(pyobj.typecode)
        sub2 = pyobj2.Actor
        
        # check parsed out correct type
        self.failUnless(isinstance(sub2.typecode, sub.typecode.__class__), 
            'local element actor "%s" must be an instance of "%s"'%
                (sub2.typecode, sub.typecode.__class__))
        
        # check local element is derived from base
        base = GTD('urn:test', 'BaseActor')
        self.failUnless(isinstance(sub2.typecode, base), 
            'local element actor must be a derived type of "%s"'%
                base)
        

if __name__ == "__main__" :
    main()

