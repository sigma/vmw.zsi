#!/usr/bin/python2

#standard imports
import syslog, sys

#domain specific imports
sys.path.insert (1, '..')
import SOAPpy

SOAPpy.Config.unwrap_results=1

class test_service:
    def test_integer(self,pass_integer):
        print type(pass_integer)
        return pass_integer

    def test_string(self,pass_string):
        print type(pass_string)
        return pass_string

    def test_float(self,pass_float):
        print type(pass_float)
        return pass_float

    def test_tuple(self,pass_tuple):
        return_tuple = SOAPpy.Types.simplify(pass_tuple)
        print type(return_tuple)
        return return_tuple

    def test_list(self,pass_list):
        print type(pass_list)
        return pass_list

    def test_dictionary(self,pass_dictionary):
        print type(pass_dictionary)
        return pass_dictionary





    
                   
                 
server = SOAPpy.SOAPServer(("localhost",9999))

access_object = test_service()
server.registerObject(access_object)
server.serve_forever()
