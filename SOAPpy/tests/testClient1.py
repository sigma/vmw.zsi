import gc
import socket
import threading
import time
import unittest
import sys
sys.path.insert(1, "..")

import SOAPpy

# global to shut down server
quit = 0

def echo(s):
    return s + s # repeats a string twice

def kill():
    global quit
    quit = 1

def server1():
    server = SOAPpy.Server.SOAPServer(addr=('127.0.0.1', 8000))
    server.registerFunction(echo)
    server.registerFunction(kill)
    global quit
    while not quit: 
        server.handle_request()

class ClientTestCase(unittest.TestCase):

    server = None
    startup_timeout = 5 # seconds

    def setUp(self):
        '''This is run once before each unit test.'''

        serverthread = threading.Thread(target=server1, name="SOAPServer")
        serverthread.start()

        start = time.time()
        connected = False
        while not connected and time.time() - start < self.startup_timeout:
            try:
                self.server = SOAPpy.Client.SOAPProxy('127.0.0.1:8000')
                self.server.echo('Hello World')
                connected = True
                time.sleep(0.1)
            except socket.error:
                pass
        
        if not connected: raise 'Server failed to start.'

    def tearDown(self):
        '''This is run once after each unit test.'''

        self.server.kill()
        time.sleep(5)

    def testEcho(self):
        '''Test echo function.'''

        server = SOAPpy.Client.SOAPProxy('127.0.0.1:8000')
        s = 'Hello World'
        self.assertEquals(server.echo(s), s+s)


    def testNoLeak(self):
        '''Test for memory leak.'''

        gc.set_debug(gc.DEBUG_SAVEALL)
        for i in range(400):
            server = SOAPpy.Client.SOAPProxy('127.0.0.1:8000')
            s = 'Hello World'
            server.echo(s)
        gc.collect()
        self.assertEquals(len(gc.garbage), 0)


if __name__ == '__main__':
    unittest.main()
