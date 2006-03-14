#!/usr/bin/env python
############################################################################
# Joshua R. Boverhof, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import os, sys, unittest
from ServiceTest import ServiceTestCase, ServiceTestSuite
from ZSI import FaultException
from ZSI.TC import _get_global_element_declaration as GED
from ZSI.writer import SoapWriter

"""
Unittest for Bug Report 
[ 1441574 ] ZSI assumes minOccurs(1) for all parts

WSDL:  
"""

CONFIG_FILE = 'config.txt'
sys.path.append('%s/%s' %(os.getcwd(), 'stubs'))

class ChoiceTest(unittest.TestCase):
    name = "test_Choice"
    done = False

    def setUp(self):
        if ChoiceTest.done: return
        ChoiceTest.done = True
        wsdl = os.path.abspath('test_Choice.xsd').strip()
        fin,fout = os.popen4('cd stubs; wsdl2py.py -x -b -f %s' %wsdl)
        # TODO: wait for wsdl2py.py to finish.
        for i in fout: print i
        import test_Choice_xsd_services_types
 
    def tearDown(self):
        pass

    def test_choice_default_facets_legal1(self):
        """<choice minOccurs=1 maxOccurs=1>
        """
        pyobj = GED("urn:example", "Easy").pyclass()
        pyobj.Rank = 1
        sw = SoapWriter()
        sw.serialize(pyobj)
        print str(sw)

    def test_choice_maxOccurs_unbounded(self):
        """<choice minOccurs=1 maxOccurs=unbounded>
        """
        pyobj = GED("urn:example", "Hard").pyclass()
        pyobj.Name = "steve"
        pyobj.Name.append("mark")
        pyobj.Any = "whatever"
        pyobj.Rank = 2
        pyobj.Rank.append(3)
        pyobj.Rank.append(4)
        sw = SoapWriter()
        sw.serialize(pyobj)
        print str(sw)



def makeTestSuite():
    suite = ServiceTestSuite()
    suite.addTest(unittest.makeSuite(ChoiceTest, "test_", suiteClass=ServiceTestSuite))
    return suite


if __name__ == "__main__" :
    unittest.TestProgram(defaultTest="makeTestSuite")

