###########################################################################
# Joshua R. Boverhof, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################

import vmw.ZSI
from vmw.ZSI import TC, TCtimes, TCcompound
from vmw.ZSI.TC import TypeCode
from vmw.ZSI import _copyright, EvaluateException
from vmw.ZSI.wstools.Utility import SplitQName
from vmw.ZSI.wstools.Namespaces import SOAP, SCHEMA

###########################################################################
# Module Classes: BaseTypeInterpreter
###########################################################################

class NamespaceException(Exception): pass
class BaseTypeInterpreter:
    """Example mapping of xsd/soapenc types to zsi python types.
    Checks against all available classes in vmw.ZSI.TC.  Used in
    wsdl2python, wsdlInterpreter, and ServiceProxy.
    """

    def __init__(self):
        self._type_list = [TC.Iinteger, TC.IunsignedShort, TC.gYearMonth, \
                           TC.InonNegativeInteger, TC.Iint, TC.String, \
                           TC.gDateTime, TC.IunsignedInt, TC.Duration,\
                           TC.IpositiveInteger, TC.FPfloat, TC.gDay, TC.gMonth, \
                           TC.InegativeInteger, TC.gDate, TC.URI, \
                           TC.HexBinaryString, TC.IunsignedByte, \
                           TC.gMonthDay, TC.InonPositiveInteger, \
                           TC.Ibyte, TC.FPdouble, TC.gTime, TC.gYear, \
                           TC.Ilong, TC.IunsignedLong, TC.Ishort, \
                           TC.Token, TC.QName, vmw.ZSI.TCapache.AttachmentRef]

        self._tc_to_int = [
            vmw.ZSI.TCnumbers.IEnumeration,
            vmw.ZSI.TCnumbers.Iint,
            vmw.ZSI.TCnumbers.Iinteger,
            vmw.ZSI.TCnumbers.Ilong,
            vmw.ZSI.TCnumbers.InegativeInteger,
            vmw.ZSI.TCnumbers.InonNegativeInteger,
            vmw.ZSI.TCnumbers.InonPositiveInteger,
            vmw.ZSI.TC.Integer,
            vmw.ZSI.TCnumbers.IpositiveInteger,
            vmw.ZSI.TCnumbers.Ishort]

        self._tc_to_float = [
            vmw.ZSI.TC.Decimal,
            vmw.ZSI.TCnumbers.FPEnumeration,
            vmw.ZSI.TCnumbers.FPdouble,
            vmw.ZSI.TCnumbers.FPfloat]

        self._tc_to_string = [
            vmw.ZSI.TC.Base64String,
            vmw.ZSI.TC.Enumeration,
            vmw.ZSI.TC.HexBinaryString,
            vmw.ZSI.TCnumbers.Ibyte,
            vmw.ZSI.TCnumbers.IunsignedByte,
            vmw.ZSI.TCnumbers.IunsignedInt,
            vmw.ZSI.TCnumbers.IunsignedLong,
            vmw.ZSI.TCnumbers.IunsignedShort,
            vmw.ZSI.TC.String,
            vmw.ZSI.TC.URI,
            vmw.ZSI.TC.XMLString,
            vmw.ZSI.TC.Token,
            vmw.ZSI.TCapache.AttachmentRef]

        self._tc_to_tuple = [
            vmw.ZSI.TC.Duration,
            vmw.ZSI.TC.QName,
            vmw.ZSI.TCtimes.gDate,
            vmw.ZSI.TCtimes.gDateTime,
            vmw.ZSI.TCtimes.gDay,
            vmw.ZSI.TCtimes.gMonthDay,
            vmw.ZSI.TCtimes.gTime,
            vmw.ZSI.TCtimes.gYear,
            vmw.ZSI.TCtimes.gMonth,
            vmw.ZSI.TCtimes.gYearMonth]

        return

    def _get_xsd_typecode(self, msg_type):
        untaged_xsd_types = {'boolean':TC.Boolean,
            'decimal':TC.Decimal,
            'base64Binary':TC.Base64String}
        if untaged_xsd_types.has_key(msg_type):
            return untaged_xsd_types[msg_type]
        for tc in self._type_list:
            if tc.type == (SCHEMA.XSD3,msg_type):
                break
        else:
            tc = TC.AnyType
        return tc

    def _get_soapenc_typecode(self, msg_type):
        if msg_type == 'Array':
            return TCcompound.Array
        if msg_type == 'Struct':
            return TCcompound.Struct

        return self._get_xsd_typecode(msg_type)

    def get_typeclass(self, msg_type, targetNamespace):
        prefix, name = SplitQName(msg_type)
        if targetNamespace in SCHEMA.XSD_LIST:
            return self._get_xsd_typecode(name)
        elif targetNamespace in [SOAP.ENC]:
            return self._get_soapenc_typecode(name)
        elif targetNamespace in  [vmw.ZSI.TCapache.Apache.NS]:
            #maybe we have an AXIS attachment
            if name == vmw.ZSI.TCapache.AttachmentRef.type[1]:
                #we have an AXIS attachment
                return vmw.ZSI.TCapache.AttachmentRef
            else:
                #AXIS Map type
                return TC.AnyType
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
        elif tc in self._tc_to_tuple:
            return 'tuple'
        elif tc in [TCcompound.Array]:
            return 'list'
        elif tc in [TC.Boolean]:
            return 'bool'
        elif isinstance(tc, TypeCode):
            raise EvaluateException,\
               'failed to map zsi typecode to a python type'
        return None


