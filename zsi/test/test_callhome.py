#!/usr/bin/env python
import os,unittest
from ZSI import version
from ZSI.wstools.logging import gridLog

os.environ['GRIDLOG_ON'] = '1'
os.environ['GRIDLOG_DEST'] = "gridlog-udp://portnoy.lbl.gov:15100"


class TestCase(unittest.TestCase):
    def ping(self):
        gridLog(program="test_callhome.py", zsi="v%d.%d.%d" % version.Version, event="ping")

def makeTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCase, "ping"))
    return suite

def main():
    unittest.main(defaultTest="makeTestSuite")

if __name__ == '__main__': 
    main()

