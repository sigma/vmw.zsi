###########################################################################
# Joshua R. Boverhof, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################
import types, copy
import ZSI
from ZSI import TC, TCtimes, TCcompound
from ZSI.TC import TypeCode
from ZSI import _copyright, _children, _child_elements, \
        _inttypes, _stringtypes, _seqtypes, _find_arraytype, _find_href, \
        _find_type, \
        EvaluateException 
from ZSI.TCcompound import _check_typecode_list,_find_arrayoffset , \
     _find_arrayposition,_offset_pat,_position_pat

from xml.dom.ext import SplitQName
from xml.ns import SOAP, SCHEMA

DEBUG  = 0
def print_debug(msg, level=1, *l, **kw):
    if DEBUG >= level:
        for i in l:
            msg += '\n*\t' + str(i)
        for k,v in kw.items():
            msg += '\n**\t%s: %s' %(k,v)
        print 'TYPECODES(%d): %s' %(level,msg)

###########################################################################
# Module Classes: BaseTypeInterpreter
###########################################################################

TC.Boolean.tag = 'boolean'
TCcompound.Array.tag = 'array'
TC.Decimal.tag = 'decimal'
TC.Base64String.tag = 'base64Binary'

class NamespaceException(Exception): pass
class BaseTypeInterpreter:
    """
    Example mapping of xsd/soapenc types to zsi python types.
    Checks against all available classes in ZSI.TC
    Used in TypeCodeSequenceGenerator, and TC_Template.
    """

    def __init__(self):
        self._type_list = [TC.Boolean, TC.Iinteger, TC.IunsignedShort, \
                           TC.gYearMonth, TC.Base64String, \
                           TC.InonNegativeInteger, TC.Iint, TC.String, \
                           TC.gDateTime, TC.IunsignedInt, \
                           TC.IpositiveInteger, TC.FPfloat, TC.gDay, \
                           TC.InegativeInteger, TC.gDate, TC.URI, \
                           TC.HexBinaryString, TC.IunsignedByte, \
                           TC.gMonthDay, TC.InonPositiveInteger, \
                           TC.Ibyte, TC.FPdouble, TC.gTime, TC.gYear, \
                           TC.Ilong, TC.IunsignedLong, TC.Ishort, \
                           TC.Decimal]

        self._tc_to_int = [
            ZSI.TCnumbers.IEnumeration,
            ZSI.TCnumbers.Iint,
            ZSI.TCnumbers.Iinteger,
            ZSI.TCnumbers.Ilong,
            ZSI.TCnumbers.InegativeInteger,
            ZSI.TCnumbers.InonNegativeInteger,
            ZSI.TCnumbers.InonPositiveInteger,
            ZSI.TC.Integer,
            ZSI.TCnumbers.IpositiveInteger,
            ZSI.TCnumbers.Ishort]
  
        self._tc_to_float = [
            ZSI.TC.Decimal,
            ZSI.TCnumbers.FPEnumeration,
            ZSI.TCnumbers.FPdouble,
            ZSI.TCnumbers.FPfloat]
        
        self._tc_to_string = [
            ZSI.TC.Base64String,
            ZSI.TC.Enumeration,
            ZSI.TC.HexBinaryString,
            ZSI.TCnumbers.Ibyte,
            ZSI.TCnumbers.IunsignedByte,
            ZSI.TCnumbers.IunsignedInt,
            ZSI.TCnumbers.IunsignedLong,
            ZSI.TCnumbers.IunsignedShort,
            ZSI.TC.String,
            ZSI.TC.URI,
            ZSI.TC.XMLString]

        self._tc_to_date = [
            ZSI.TCtimes.gDate,
            ZSI.TCtimes.gDateTime,
            ZSI.TCtimes.gDay,
            ZSI.TCtimes.gMonthDay,
            ZSI.TCtimes.gTime,
            ZSI.TCtimes.gYear,
            ZSI.TCtimes.gYearMonth]
        
        return
    
    def _get_xsd_typecode(self, msg_type):
        for tc in self._type_list:
            if tc.tag == msg_type:
                break
        else:
            tc = TC.Any
        return tc

    def _get_soapenc_typecode(self, msg_type):
        if msg_type == 'Array':
            return TCcompound.Array
        elif msg_type == 'base64':
            return TC.Base64String
        else:
            raise NamespaceException

    def get_typeclass(self, msg_type, targetNamespace):
        prefix, name = SplitQName(msg_type)
        if targetNamespace in SCHEMA.XSD_LIST:
            return self._get_xsd_typecode(name)
        elif targetNamespace in [SOAP.ENC]:
            return self._get_soapenc_typecode(name)
        return None

    def get_pythontype(self, msg_type, targetNamespace, typeclass=None):
        if not typeclass:
            tc = self.get_typeclass(msg_type, targetNamespace)
        else:
            tc = typeclass
        if tc in self._tc_to_int:
            return 'int'
        elif tc in self._tc_to_float:
            return 'float'
        elif tc in self._tc_to_string:
            return 'str'
        elif tc in self._tc_to_date:
            return 'tuple'
        elif tc in [TCcompound.Array]:
            return 'list'
        elif tc in [TC.Boolean]:
            return 'boolean'
        elif isinstance(tc, TypeCode):
            raise EvaluateException,\
               'failed to map zsi typecode to a python type'
        return None


