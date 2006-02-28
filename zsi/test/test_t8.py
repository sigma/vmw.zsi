#!/usr/bin/env python
import unittest, sys
from ZSI import *


class t8TestCase(unittest.TestCase):
    "Test Any serialize and parse"

    def check_parse_empty_all(self):
        # None
        skip = [TC.FPEnumeration, TC.Enumeration, TC.IEnumeration, TC.List, TC.Integer]
        for typeclass in filter(lambda c: type(c) in [types.ClassType,type] and not issubclass(c, TC.String) and issubclass(c, TC.SimpleType), TC.__dict__.values()):
            if typeclass in skip: continue
            tc = typeclass()
            sw = SoapWriter()
            sw.serialize(None, typecode=tc, typed=True)
            soap = str(sw)
            ps = ParsedSoap(soap)
            parsed = ps.Parse(Any())
            self.assertEqual(None, parsed)

    def check_parse_empty_string(self):
        # Empty String
        typecodes = TC.Any.parsemap.values()
        for tc in filter(lambda c: isinstance(c, TC.String), TC.Any.parsemap.values()):
            sw = SoapWriter()
            sw.serialize("", typecode=tc, typed=True)
            soap = str(sw)
            print 
            print soap
            ps = ParsedSoap(soap)
            parsed = ps.Parse(Any())
            self.assertEqual("", parsed)

    def check_builtins(self):
        typecode = Any(type=True)
        myInt,myLong,myStr,myDate,myFloat = 123,2147483648,\
            u"hello", time.gmtime(), 1.0001
        orig = [myInt,myLong,myStr,myDate,myFloat]

        sw = SoapWriter()
        sw.serialize(orig, typecode=Any())
        print >>sys.stdout, sw
        
        ps = ParsedSoap(str(sw)) 
        parsed = ps.Parse(Any())
        self.assertEqual(len(orig), len(parsed))

        self.assertEqual(myInt, parsed[0])
        self.assertEqual(myLong, parsed[1])
        self.assertEqual(myStr, parsed[2])
        self.assertEqual(myDate[0:6], parsed[3][0:6])
        self.assertEqual(myFloat, parsed[4])
        
        self.assertEqual(type(myInt), type(parsed[0]))
        self.assertEqual(type(myLong), type(parsed[1]))
        self.assertEqual(type(myStr), type(parsed[2]))
        self.assertEqual(tuple, type(parsed[3]))
        self.assertEqual(type(myFloat), type(parsed[4]))

def makeTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(t8TestCase, "check"))
    return suite

def main():
    unittest.main(defaultTest="makeTestSuite")


if __name__ == "__main__" : main()


