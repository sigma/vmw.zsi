#!/usr/bin/python

from SOAPpy import SOAP
server = SOAP.SOAPProxy("http://206.135.217.234:8000/")
server.COM_SetProperty("Visible", 1)
server.Workbooks.Open("c:\\test.xls")
server.COM_NestedCall('ActiveSheet.Range("A2").EntireRow.Delete()')
server.quit()







