
default: echoClient echoHeader largeDataTest Bug1001646 Bug916265 \
	 card independent \
         testClient1 outside_services

echoClient: 
	python echoServer.py >& echoServer_echoClient.log &
	sleep 5s # wait for server to start up
	python echoClient.py

echoHeader:
	python echoServer.py >& echoServer_echoHeader.log &
	sleep 5s # wait for server to start up
	python echoHeader.py

largeDataTest:
	python echoServer.py >& echoServer_largeDataTest.log &
	sleep 5s # wait for server to start up
	python largeDataTest.py

card:
	python cardServer.py >& cardServer.log &
	sleep 5s # wait for server to start up
	python cardClient.py

esj:
	python esj_test_server.py >& esj_test.log &
	python esj_test_client.py


Bug1001646:
	python echoServer.py >& echoServer_largeDataTest.log &
	sleep 5s # wait for server to start up
	python Bug1001646.py

Bug916265:
	python echoServer.py >& echoServer_Bug916265.log &
	sleep 5s # wait for server to start up
	python Bug916265.py

outside_services:
	python alanbushTest.py
	python BabelfishWSDLTest.py
	python GoogleTest.py
	python quoteTest.py
	python simpleWSDL.py
	python testWSDL.py

independent:
	python speedTest.py
	python Bug918216.py
	python ComplexTypes.py
	-python SOAPtest.py # one subtest will fail
	python TCtest.py
	python testleak.py
	python translateTest.py
	python weatherTest.py
	python whoisTest.py
	python xmethods.py
	python ZeroLengthArray.py

testClient1:
	python testClient1.py

broken:
	python newsTest.py
	python excelTest.py
	python storageTest.py
