#! /usr/bin/env python

WSDL_DEFINITION = '''<?xml version="1.0"?>

<definitions name="InteropTest"
    targetNamespace="http://soapinterop.org/" 
    xmlns="http://schemas.xmlsoap.org/wsdl/" 
    xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" 
    xmlns:tns="http://soapinterop.org/">

  <import
      location="http://www.whitemesa.com/interop/InteropTest.wsdl"
      namespace="http://soapinterop.org/xsd"/>
  <import
      location="http://www.whitemesa.com/interop/InteropTest.wsdl"
      namespace="http://soapinterop.org/"/>
  <import
      location="http://www.whitemesa.com/interop/InteropTestB.wsdl"
      namespace="http://soapinterop.org/"/>
  <import
      location="http://www.whitemesa.com/interop/echoHeaderBindings.wsdl"
      namespace="http://soapinterop.org/"/>

  <service name="interop">
    <port name="TestSoap" binding="tns:InteropTestSoapBinding">
      <soap:address location=">>>URL<<<"/>
    </port>
    <port name="TestSoapB" binding="tns:InteropTestSoapBindingB">
      <soap:address location=">>>URL<<<"/>
    </port>
    <port name="EchoHeaderString" binding="tns:InteropEchoHeaderStringBinding">
      <soap:address location=">>>URL<<<"/>
    </port>
    <port name="EchoHeaderStruct" binding="tns:InteropEchoHeaderStructBinding">
      <soap:address location=">>>URL<<<"/>
    </port>
  </service>

</definitions>
'''

from ZSI import *
from ZSI import _copyright, _seqtypes
import types

class SOAPStruct:
    def __init__(self, name):
	pass
    def __str__(self):
	return str(self.__dict__)

def SimpleTypetoStruct(*args):
    s = SOAPStruct(None)
    s.varString, s.varInteger, s.varFloat = args
    return s

class TC_SOAPStruct(TC.Struct):
    def __init__(self, pname=None, **kw):
	TC.Struct.__init__(self, SOAPStruct, [
	    TC.String('varString', strip=0, inline=1),
	    TC.Integer('varInt'),
	    TC.FPfloat('varFloat'),
	], pname, **kw)

class TC_SOAPStructStruct(TC.Struct):
    def __init__(self, pname=None, **kw):
	TC.Struct.__init__(self, SOAPStruct, [
	    TC.String('varString', strip=0),
	    TC.Integer('varInt'),
	    TC.FPfloat('varFloat'),
	    TC_SOAPStruct('varStruct'),
	], pname, **kw)

class TC_SOAPArrayStruct(TC.Struct):
    def __init__(self, pname=None, **kw):
	TC.Struct.__init__(self, SOAPStruct, [
	    TC.String('varString', strip=0),
	    TC.Integer('varInt'),
	    TC.FPfloat('varFloat'),
	    TC.Array('string', TC.String(), 'varArray'),
	], pname, **kw)

class TC_ArrayOfstring(TC.Array):
    def __init__(self, pname=None, **kw):
	TC.Array.__init__(self, 'string', TC.String(), pname, **kw)

class TC_ArrayOfint(TC.Array):
    def __init__(self, pname=None, **kw):
	TC.Array.__init__(self, 'int', TC.Integer(), pname, **kw)

class TC_ArrayOffloat(TC.Array):
    def __init__(self, pname=None, **kw):
	TC.Array.__init__(self, 'float', TC.FPfloat(), pname, **kw)

class TC_ArrayOfSOAPStruct(TC.Array):
    def __init__(self, pname=None, **kw):
	TC.Array.__init__(self, 'Z:SOAPStruct', TC_SOAPStruct(), pname, **kw)

#class TC_ArrayOfstring2D(TC.Array):
#    def __init__(self, pname=None, **kw):
#	TC.Array.__init__(self, 'string', TC.String(), pname, **kw)

class RPCParameters:
    def __init__(self, name):
	pass
    def __str__(self):
	t = str(self.__dict__)
	if hasattr(self, 'inputStruct'):
	    t += '\ninputStruct\n'
	    t += str(self.inputStruct)
	if hasattr(self, 'inputStructArray'):
	    t += '\ninputStructArray\n'
	    t += str(self.inputStructArray)
	return t

class Operation:
    dispatch = {}
    SOAPAction = '''"http://soapinterop.org/"'''
    ns = "http://soapinterop.org/"
    hdr_ns = "http://soapinterop.org/echoheader/"

    def __init__(self, name, tcin, tcout, **kw):
	self.name = name
	if type(tcin) not in _seqtypes: tcin = tcin,
	self.TCin = TC.Struct(RPCParameters, tuple(tcin), name)
	if type(tcout) not in _seqtypes: tcout = tcout,
	self.TCout = TC.Struct(RPCParameters, tuple(tcout), name + 'Response')
	self.convert = kw.get('convert', None)
	self.headers = kw.get('headers', [])
	Operation.dispatch[name] = self

Operation("echoString",
    TC.String('inputString'),
    TC.String('inputString', oname='return')
)
Operation("echoStringArray",
    TC_ArrayOfstring('inputStringArray'),
    TC_ArrayOfstring('inputStringArray', oname='return')
)
Operation("echoInteger",
    TC.Integer('inputInteger'),
    TC.Integer('inputInteger', oname='return'),
)
Operation("echoIntegerArray",
    TC_ArrayOfint('inputIntegerArray'),
    TC_ArrayOfint('inputIntegerArray', oname='return'),
)
Operation("echoFloat",
    TC.FPfloat('inputFloat'),
    TC.FPfloat('inputFloat', oname='return'),
)
Operation("echoFloatArray",
    TC_ArrayOffloat('inputFloatArray'),
    TC_ArrayOffloat('inputFloatArray', oname='return'),
)
Operation("echoStruct",
    TC_SOAPStruct('inputStruct'),
    TC_SOAPStruct('inputStruct', oname='return'),
)
Operation("echoStructArray",
    TC_ArrayOfSOAPStruct('inputStructArray'),
    TC_ArrayOfSOAPStruct('inputStructArray', oname='return'),
)
Operation("echoVoid",
    [],
    [],
    headers=( ( Operation.hdr_ns, 'echoMeStringRequest' ),
		( Operation.hdr_ns, 'echoMeStructRequest' ) )
)
Operation("echoBase64",
    TC.Base64String('inputBase64'),
    TC.Base64String('inputBase64', oname='return'),
)
Operation("echoDate",
    TC.gDateTime('inputDate'),
    TC.gDateTime('inputDate', oname='return'),
)
Operation("echoHexBinary",
    TC.HexBinaryString('inputHexBinary'),
    TC.HexBinaryString('inputHexBinary', oname='return'),
)
Operation("echoDecimal",
    TC.Decimal('inputDecimal'),
    TC.Decimal('inputDecimal', oname='return'),
)
Operation("echoBoolean",
    TC.Boolean('inputBoolean'),
    TC.Boolean('inputBoolean', oname='return'),
)
Operation("echoStructAsSimpleTypes",
    TC_SOAPStruct('inputStruct'),
    ( TC.String('outputString'), TC.Integer('outputInteger'),
	TC.FPfloat('outputFloat') ),
    convert=lambda s: (s.varString, s.varInt, s.varFloat),
)
Operation("echoSimpleTypesAsStruct",
    ( TC.String('inputString'), TC.Integer('inputInteger'),
	TC.FPfloat('inputFloat') ),
    TC_SOAPStruct('return'),
    convert=SimpleTypetoStruct
)
#Operation("echo2DStringArray",
#    TC_ArrayOfstring2D('input2DStringArray'),
#    TC_ArrayOfstring2D('return')
#),
Operation("echoNestedStruct",
    TC_SOAPStructStruct('inputStruct'),
    TC_SOAPStructStruct('inputStruct', oname='return'),
)
Operation("echoNestedArray",
    TC_SOAPArrayStruct('inputStruct'),
    TC_SOAPArrayStruct('inputStruct', oname='return'),
)
