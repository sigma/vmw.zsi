#!/usr/bin/env python

# Copyright (c) 2001 actzero, inc. All rights reserved.

import sys, os, time, signal

sys.path.insert (1, '..')

from SOAPpy import SOAP

ident = '$Id$'

#PROXY="http://data.ourfavoritesongs.com"
PROXY="http://localhost:15500"
EMAIL="bennett@actzero.com"
NAME="Bennett"
PASSWORD="mypasswd"

MY_PORT=15600

def resourceChanged (url):
    print "\n##### NOTIFICATION MESSAGE: Resource %s has changed #####\n" % url
    return SOAP.booleanType(1)

def printstatus (cmd, stat):
    print
    if stat.flError:
    	print "### %s failed: %s ###" % (cmd, stat.message)
    else:
        print "### %s successful: %s ###" % (cmd, stat.message)
    return not stat.flError

server = SOAP.SOAPProxy(encoding="US-ASCII", 
	proxy=PROXY,
	soapaction="/xmlStorageSystem"
	)
#	, config=SOAP.SOAPConfig(debug=1))

# Register as a new user or update user information
reg = server.registerUser(email=EMAIL, name=NAME, password=PASSWORD, clientPort=MY_PORT, userAgent=SOAP.SOAPUserAgent())
printstatus("registerUser", reg)

# See what this server can do
reg = server.getServerCapabilities (email=EMAIL, password=PASSWORD)
if printstatus("getServerCapabilities", reg):
    print "Legal file extensions: " + str(reg.legalFileExtensions)
    print "Maximum file size: " + str(reg.maxFileSize)
    print "Maximum bytes per user: " + str(reg.maxBytesPerUser)
    print "Number of bytes in use by the indicated user: " + str(reg.ctBytesInUse)
    print "URL of the folder containing your files: " + str(reg.yourUpstreamFolderUrl)

# Store some files
reg = server.saveMultipleFiles (email=EMAIL, password=PASSWORD, 
	relativepathList=['index.html','again.html'], 
	fileTextList=['<html><title>bennett@actzero.com home page</title><body>' + 
			'<a href=again.html>Hello Earth</a></body></html>',
			'<html><title>bennett@actzero.com home page</title><body>' + 
			'<a href=index.html>Hello Earth Again</a></body></html>'])
if printstatus("saveMultipleFiles", reg):
    print "Files stored:"
    for file in reg.urlList:
    	print "    %s" % file

    # Save this for call to test pleaseNotify
    mylist = reg.urlList
else:
    mylist = []

# Check to see what files are stored
reg = server.getMyDirectory (email=EMAIL, password=PASSWORD)
if printstatus("getMyDirectory", reg):
    i = 1
    while hasattr(reg.directory, "file%05d" % i):
    	d = getattr(reg.directory, "file%05d" % i)
	print "Relative Path: %s" % d.relativePath
	print "Size: %d" % d.size
	print "Created: %s" % d.whenCreated
	print "Last Uploaded: %s" % d.whenLastUploaded
	print "URL: %s" % d.url
	print
	i += 1

# Set up notification
reg = server.pleaseNotify(notifyProcedure="resourceChanged", port=MY_PORT, path="/", protocol="soap", urlList=mylist)
printstatus("notifyProcedure", reg)

pid = os.fork()
if pid == 0:
    # I am a child process.  Set up SOAP server to receive notification
    print
    print "## Starting notification server ##"

    s = SOAP.SOAPServer(('localhost', MY_PORT))
    s.registerFunction(resourceChanged)
    s.serve_forever()

else:

    def handler(signum, frame):
	# Kill child process
	print "Killing child process %d" % pid
    	os.kill(pid, signal.SIGINT)

    signal.signal(signal.SIGINT, handler)

    # I am a parent process
    # Change some files
    time.sleep(3)
    reg = server.saveMultipleFiles (email=EMAIL, password=PASSWORD, 
		relativepathList=['index.html'], 
		fileTextList=['<html><title>bennett@actzero.com home page</title><body>' + 
			'<a href=again.html>Hello Bennett</a></body></html>'])
    if printstatus("saveMultipleFiles", reg):
    	print "Files stored:"
    	for file in reg.urlList:
    	    print "    %s" % file

    os.waitpid(pid, 0)
