#!/usr/bin/python2

#standard imports
import syslog, sys

#domain specific imports
sys.path.insert (1, '..')
import SOAPpy

SOAPpy.Config.unwrap_results=0
 
##     def test_integer(self,pass_integer):
##     def test_string(self,pass_string):
##     def test_float(self,pass_float):
##     def test_tuple(self,pass_tuple):
##     def test_list(self,pass_list):
##     def test_dictionary(self,pass_dictionary):



if __name__ == "__main__":

    server = SOAPpy.SOAPProxy("http://localhost:9999")

    original_integer = 5
    result_integer = server.test_integer(original_integer)
    print "original_integer %s" % original_integer
    print "result_integer %s" % result_integer
    
    original_string = "five"
    result_string = server.test_string(original_string)
    print "original_string %s" % original_string
    print "result_string %s" % result_string
    
    original_float = 5.0
    result_float = server.test_float(original_float)
    print "original_float %s" % original_float
    print "result_float %s" % result_float
    
    original_tuple = (1,2,"three","four",5)
    simplified_tuple = SOAPpy.Types.simplify(original_tuple)
    #result_tuple = server.test_tuple(original_tuple)

    result_tuple = server.test_tuple(original_tuple)

    print "original_tuple %s" % (str(original_tuple))
    print "result_tuple %s" % (str(result_tuple))

    print dir(result_tuple)
    print result_tuple.data
    
    original_list = [5,4,"three",2,1]
    result_list = server.test_list(original_list)
    print "original_list %s" % original_list
    print "result_list %s" % result_list
    
    original_dictionary = {
        'one': 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        }
    result_dictionary = server.test_dictionary(original_dictionary)
    print "original_dictionary %s" % original_dictionary
    print "result_dictionary %s" % result_dictionary
    
