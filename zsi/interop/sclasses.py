#! /usr/bin/env python

from ZSI import *
from ZSI import _copyright
import types

_textprotect = lambda s: s.replace('&', '&amp;').replace('<', '&lt;')

class Testclass:
    def __init__(self, name):
	self.name = name or '-Noname-'
    def __str__(self):
	'''String format -- XML-syntax dump of all attributes.'''
	ret = '<%s>\n' % self.name
	for k,v in self.__dict__.items():
	    if k == 'name': continue
	    t = type(v)
	    tstr = str(t)
	    if tstr[:6] == '<type ' and tstr[-1] == '>': tstr = tstr[6:-1]
	    tstr = _textprotect(tstr)
	    if t in [ types.ListType, types.TupleType]:
		ret += '   <item name="%s" pytype="%s">\n' % (k, tstr)
		for e in v: ret += str(e)
		ret += '   </item>\n'
	    else:
		if t == types.UnicodeType: v = v.encode('utf-8')
		ret += '   <item name="%s" pytype="%s">%s\n  </item>\n' % \
		    (k, tstr, str(v))
	ret += '</%s>\n' % self.name
	return ret

TC_void = TC.Struct(Testclass, [
])

TC_string = TC.Struct(Testclass, [
    TC.String("inputString", strip=0),
])

TC_base64 = TC.Struct(Testclass, [
    TC.Base64String('inputBase64'),
])

TC_hexBinary = TC.Struct(Testclass, [
    TC.HexBinaryString('inputhexBinary'),
])


TC_date = TC.Struct(Testclass, [
    TC.gDateTime("inputDate"),
])

TC_boolean = TC.Struct(Testclass, [
    TC.Boolean('inputBoolean'),
])

TC_integer = TC.Struct(Testclass, [
    TC.Integer("inputInteger"),
])

TC_float = TC.Struct(Testclass, [
    TC.FPfloat("inputFloat"),
])

TC_stringarray = TC.Struct(Testclass, [
    TC.Array("SOAP-ENC:string[]", TC.String(strip=0), "inputStringArray"),
])

TC_integerarray = TC.Struct(Testclass, [
    TC.Array("SOAP-ENC:integer[]", TC.Integer(), "inputIntegerArray"),
])

TC_floatarray = TC.Struct(Testclass, [
    TC.Array("SOAP-ENC:float[]", TC.FPfloat(), "inputFloatArray"),
])

TC_soapstruct = TC.Struct(Testclass, [
    TC.Struct(Testclass, [
	TC.Integer("varInt"),
	TC.FPfloat("varFloat"),
	TC.String("varString", strip=0),
    ], "inputStruct", type=("http://soapinterop.org/xsd", "SOAPStruct"))
])

TC_soapstructarray = TC.Struct(Testclass, [
    TC.Array("Z:SOAPStruct[]",
	TC.Struct(Testclass, [
	    TC.Integer("varInt"),
	    TC.FPfloat("varFloat"),
	    TC.String("varString", strip=0),
	]), "inputStructArray")
])

OPDICT = {
    'echoVoid':		TC_void,
    'echoDate':		TC_date,
    'echoString':	TC_string,
    'echoStringArray':	TC_stringarray,
    'echoBoolean':	TC_boolean,
    'echoInteger':	TC_integer,
    'echoDecimal':	TC_integer,
    'echoIntegerArray':	TC_integerarray,
    'echoFloat':	TC_float,
    'echoFloatArray':	TC_floatarray,
    'echoStruct':	TC_soapstruct,
    'echoStructArray':	TC_soapstructarray,
    'echoBase64':	TC_base64,
    'echohexBinary':	TC_hexBinary,
    'echoHexBinary':	TC_hexBinary,
}

if __name__ == '__main__': print _copyright
