############################################################################
# Monte M. Goode, LBNL
# See Copyright for copyright notice!
###########################################################################

import ZSI
from ZSI.typeinterpreter import BaseTypeInterpreter
from ZSI.wstools.Utility import Collection
import xml
from xml.dom.ext import SplitQName

###########################################################################
# "Virtual" superclasses for the wsdl adapters
###########################################################################


class WsdlInterface:
    """Inteface to Wsdl class which contains one wsdl definition
    """
    def __init__(self, wsdl):
        self._wsdl = wsdl

    def getName(self):
        """return name of definition, or None
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getServicesDict(self):
        """return dictionary of service adapter objects
           {name:service_obj}
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getServicesList(self):
        """return listof service adapter objects
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getSchemaDict(self):
        """return dictionary of schema adapter objects
           {namespace:schema}
        """
        raise NotImplementedError, 'abstract method not implemented'


class ServiceInterface:
    """Inteface to service class
    """
    def __init__(self, service):
        self._service = service

    def getName(self):
        """return name of definition, or None
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getPortList(self):
        """return list of ports or []
        """
        raise NotImplementedError, 'abstract method not implemented'

class PortInterface:
    """Inteface to port class
    """
    def __init__(self, port):
        self._port = port

    def getName(self):
        """returns port name
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getExtensions(self):
        """returns extensions obj
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getBinding(self):
        """returns binding obj
        """
        raise NotImplementedError, 'abstract method not implemented'

class BindingInterface:
    """Inteface to binding class
    """
    def __init__(self, binding):
        self._binding = binding

    def getOperationDict(self):
        """returns list of operation objs
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getPortType(self):
        """returns portType object
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getExtensions(self):
        """get binding extensions
        """
        raise NotImplementedError, 'abstract method not implemented'
    
    def getSoapBinding(self):
        """return binding soap binding
        """
        raise NotImplementedError, 'abstract method not implemented'

class PortTypeInterface:
    """Inteface to portType class
    """
    def __init__(self, portType):
        self._portType = portType

    def getName(self):
        """return name of portType, or None
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getOperationList(self):
        """returns list of operation objs
        """
        raise NotImplementedError, 'abstract method not implemented'


class OperationInterface:
    """Inteface to operation class
    """
    def __init__(self, operation):
        self._operation = operation

    def getName(self):
        """return name of operation, or None
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getInput(self):
        """return input obj
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getOutput(self):
        """return output obj
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getFaultList(self):
        """return list of fault objs
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getExtensions(self):
        """return extensions
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getSoapBinding(self):
        """return op soap binding
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getSoapOperation(self):
        """return op soap operation
        """
        raise NotImplementedError, 'abstract method not implemented'

class InputInterface:
    """Inteface to input class
    """
    def __init__(self, input):
        self._input = input

    def getMessage(self):
        """return message obj
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getExtensions(self):
        """return extensions
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getSoapBody(self):
        """return input soap body
        """
        raise NotImplementedError, 'abstract method not implemented'

class OutputInterface:
    """Inteface to output class
    """
    def __init__(self, output):
        self._output = output

    def getMessage(self):
        """return message obj
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getExtensions(self):
        """return extensions
        """
        raise NotImplementedError, 'abstract method not implemented'

class FaultInterface:
    """Inteface to fault class
    """
    def __init__(self, fault):
        self._fault = fault

    def getName(self):
        """fault name
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getMessage(self):
        """fault message
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getExtensions(self):
        """return extensions
        """
        raise NotImplementedError, 'abstract method not implemented'
 
class ExtensionsInterface:
    pass

class ExtensionFactory:
    def __init__(self, extObj):
        self._extObj = extObj

    def getExtension(self):
        raise NotImplementedError, 'abstract method not implemented'

class SoapBindingInterface:
    """Interface to Soap bindings
    """
    def __init__(self, binding):
        self._binding = binding

    def getStyle(self):
        """Binding style
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getTransport(self):
        """Binding transport
        """
        raise NotImplementedError, 'abstract method not implemented'

class SoapOperationInterface:
    """Interface to Soap ops
    """
    def __init__(self, operation):
        self._operation = operation

    def getAction(self):
        """Operation action
        """
        raise NotImplementedError, 'abstract method not implemented'

class SoapBodyInterface:
    """Interface to Soap Body
    """
    def __init__(self, body):
        self._body = body

    def getUse(self):
        """Body Use
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getNamespace(self):
        """Body Namespace
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getEncoding(self):
        """Body Encoding
        """
        raise NotImplementedError, 'abstract method not implemented'

class SoapAddressInterface:
    """Interface to Soap Addresses
    """
    def __init__(self, address):
        self._address = address

    def getLocation(self):
        """Address Location
        """
        raise NotImplementedError, 'abstract method not implemented'

class SoapFaultInterface:
    """Interface to Soap faults
    """
    def __init__(self, fault):
        self._fault = fault

    def getName(self):
        """Fault name
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getUse(self):
        """Fault Use
        """
        raise NotImplementedError, 'abstract method not implemented'

class MessageInterface:
    """Inteface to message class
    """
    def __init__(self, message):
        self._message = message

    def getName(self):
        """return name of message, or None
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getPartList(self):
        """return list of parts
        """
        raise NotImplementedError, 'abstract method not implemented'

class PartInterface:
    """Inteface to part class
    """
    def __init__(self, part):
        self._part = part

    def getName(self):
        """return name of part, or None
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getElement(self):
        """return part's element or None
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getType(self):
        """return part's type or None
        """
        raise NotImplementedError, 'abstract method not implemented'

class TypeInterface:
    """Inteface to type class
    """
    def __init__(self, obj):
        self._type = obj

    def getName(self):
        """return name of part, or None
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getTargetNamespace(self):
        """return targetnamespace of type
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getQName(self):
        """return type's qname
        """
        raise NotImplementedError, 'abstract method not implemented'

    def isSimpleType(self):
        """Boolean - true if simple type
        """
        raise NotImplementedError, 'abstract method not implemented'
    
    def isComplexType(self):
        """Boolean - true if complex type
        """
        raise NotImplementedError, 'abstract method not implemented'
    
    def isBasicElement(self):
        """Returns a type if is a primitive element type else None
        """
        raise NotImplementedError, 'abstract method not implemented'


###########################################################################
# "Virtual" superclasses for the schema adapters
###########################################################################

class SchemaInterface:
    """Inteface to schema class
    """
    def __init__(self, schema):
        self._schema = schema

    def getImports(self):
        """return a list of imports
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getTargetNamespace(self):
        """return targetnamespace of schema
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getXmlnsDict(self):
        """return xmlns dictionary
           {'prefix':'namespace', 'xmlns':'xmlns namespace'}
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getTypesDict(self):
        """return dictionary of all types
           {'name':type}
        """
        raise NotImplementedError, 'abstract method not implemented'


class SchemaTypeInterface:
    """Interface to schema types
    """
    def __init__(self, type):
        self._type = type

    def getName(self):
        """get the type name
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getTargetNamespace(self):
        """get the ns
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getType(self):
        """get the type
        """
        raise NotImplementedError, 'abstract method not implemented'
    
    def isSimpleType(self):
        """boolean - simple type?
        """
        raise NotImplementedError, 'abstract method not implemented'

    def isComplexType(self):
        """boolean - complex type?
        """
        raise NotImplementedError, 'abstract method not implemented'

    def isWildCard(self):
        """boolean - wild card declaration?
        """
        raise NotImplementedError, 'abstract method not implemented'

    def isElement(self):
        """boolean - an element?
        """
        raise NotImplementedError, 'abstract method not implemented'

    def isLocalElement(self):
        """boolean - a local element?
        """
        raise NotImplementedError, 'abstract method not implemented'

    def isAttribute(self):
        """boolean - an attribute?
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getDefinition(self):
        """return a SchemaDefinition object
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getDeclaration(self):
        """return a SchemaDeclaration object
        """
        raise NotImplementedError, 'abstract method not implemented'


class SchemaDefinitionInterface:
    def __init__(self, definition):
        self._def = definition

    def isDefinition(self):
        """boolean - a definition?
        """
        raise NotImplementedError, 'abstract method not implemented'

    def isDeclaration(self):
        """boolean - a declaration?
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getTargetNamespace(self):
        """get NS
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getName(self):
        """get name
        """
        raise NotImplementedError, 'abstract method not implemented'

    def isComplexType(self):
        """boolean - complex type?
        """
        raise NotImplementedError, 'abstract method not implemented'

    def isComplexContent(self):
        """boolean - complex content type?
        """
        raise NotImplementedError, 'abstract method not implemented'

    def isSimpleContent(self):
        """boolean - simple content type?
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getModelGroup(self):
        """returns a model group adapter
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getAttributes(self):
        """returns a list of attributes
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getDerivedTypes(self):
        """returns derived type adapter
        """
        raise NotImplementedError, 'abstract method not implemented'

    def isSimpleType(self):
        """boolean - simple type?
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getTypeclass(self):
        """get typeclass for simple type
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getQName(self):
        """get qname for simple type
        """
        raise NotImplementedError, 'abstract method not implemented'

    def expressLocalAsGlobal(self, tp):
        """transform a local complex type declaration to a global
        looking one.
        """
        raise NotImplementedError, 'abstract method not implemented'


class SchemaDeclarationInterface:
    def __init__(self, declaration):
        self._dec = declaration

    def isDefinition(self):
        """boolean - a definition?
        """
        raise NotImplementedError, 'abstract method not implemented'

    def isDeclaration(self):
        """boolean - a declaration?
        """
        raise NotImplementedError, 'abstract method not implemented'

    def isWildCard(self):
        """boolean - a wildcard?
        """
        raise NotImplementedError, 'abstract method not implemented'

    def isAnyType(self):
        """boolean - an any type?
        """
        raise NotImplementedError, 'abstract method not implemented'

    def isElement(self):
        """boolean - an element?
        """
        raise NotImplementedError, 'abstract method not implemented'

    def isLocalElement(self):
        """boolean - a local element?
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getName(self):
        """returns name
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getTargetNamespace(self):
        """return namespace
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getType(self):
        """return type
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getMinOccurs(self):
        """min occurs in local element dec
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getMaxOccurs(self):
        """max occurs in local element dec
        """
        raise NotImplementedError, 'abstract method not implemented'

    def isNillable(self):
        """nillable flag in local element dec
        """
        raise NotImplementedError, 'abstract method not implemented'


class ModelGroupInterface:
    def __init__(self, model, all=False, sequence=False, choice=False):
        self._model      = model
        self._all        = all
        self._sequence   = sequence
        self._choice     = choice

    def isAll(self):
        """boolean - is complexType 'all'
        """
        raise NotImplementedError, 'abstract method not implemented'

    def isChoice(self):
        """boolean - is complexType 'choice'
        """
        raise NotImplementedError, 'abstract method not implemented'

    def isSequence(self):
        """boolean - is complexType 'sequence'
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getContent(self):
        """return list of type data
        """
        raise NotImplementedError, 'abstract method not implemented'


class DerivedTypesInterface:
    def __init__(self, content, complex=False, simple=False):
        self._content = content
        self._complex = complex
        self._simple  = simple

    def isComplexContent(self):
        """boolean - is it complex content?
        """
        raise NotImplementedError, 'abstract method not implemented'

    def isSimpleContent(self):
        """boolean - is it simple content?
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getTypeclass(self):
        """get the typeclass of the derived type
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getArrayType(self):
        """return a tuple of array information
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getDerivation(self):
        """return derivation
        """
        raise NotImplementedError, 'abstract method not implemented'


###########################################################################
# Adapter classes for the XMLSchema/ZSI/wstools wsdl support
###########################################################################

class WsdlInterfaceError(Exception):
    pass


class ZSIWsdlAdapter(WsdlInterface):
    def getName(self):
        """return name of definition, or None
        """
        if self._wsdl.name:
            return self._wsdl.name
        elif self._wsdl.services:
            return self._wsdl.services[0].name
        else:
            return None

    def getServicesDict(self):
        """return dictionary of service adapter objects
           {name:service_obj}
        """
        services = {}
        for s in self._wsdl.services:
            services[s.name] = ZSIServiceAdapter(self._wsdl, s)
        return services

    def getServicesList(self):
        """return list of service adapter objects
        """
        services = []
        for s in self._wsdl.services:
            services.append(ZSIServiceAdapter(self._wsdl, s))
        return services

    def getSchemaDict(self):
        """return dictionary of schema adapter objects
        """

        schemas = {}
        
        for k in self._wsdl.types.keys():
            schemas[k] = ZSISchemaAdapter(self._wsdl.types[k])
            
        return schemas

class ZSIServiceAdapter(ServiceInterface):
    def __init__(self, ws, s):
        ServiceInterface.__init__(self, s)
        self._ws = ws
    
    def getName(self):
        """return name of service, or None
        """
        if self._service.name:
            return self._service.name
        else:
            return None

    def getPortList(self):
        """return list of ports or []
        """
        ports = []
        for p in self._service.ports.values():
            ports.append(ZSIPortAdapter(self._ws, p))
        return ports

class ZSIPortAdapter(PortInterface):
    def __init__(self, ws, p):
        PortInterface.__init__(self, p)
        self._ws = ws
        
    def getName(self):
        return self._port.name
    
    def getExtensions(self):
        """returns extensions obj
        """

        extensions = []

        for e in self._port.extensions:
            extensions.append(ZSIExtensionFactory(e).getExtension())
        
        return extensions

    def getBinding(self):
        """returns binding obj
        """
        return ZSIBindingAdapter(self._ws, self._port.getBinding())

class ZSIBindingAdapter(BindingInterface):
    def __init__(self, ws, b):
        BindingInterface.__init__(self, b)
        self._ws = ws
        
    def getName(self):
        return self._binding.name
    
    def getOperationDict(self):
        """returns list of operation objs
        """
        operations = {}
        for x,y in self._binding.operations.data.items():
            operations[x] = ZSIOperationAdapter(self._ws, y)
        return operations

    def getPortType(self):
        """returns portType object
        """
        return ZSIPortTypeAdapter(self._ws, self._binding.getPortType())

    def getExtensions(self):
        """return extensions
        """

        extensions = []

        for e in self._binding.extensions:
            extensions.append(ZSIExtensionFactory(e).getExtension())
        
        return extensions

    def getSoapBinding(self):
        """return binding soap binding
        """
        sb = None

        for e in self.getExtensions():
            if isinstance(e, ZSISoapBindingAdapter):
                sb = e

        return sb

class ZSIPortTypeAdapter(PortTypeInterface):
    def __init__(self, ws, p):
        PortTypeInterface.__init__(self, p)
        self._ws = ws
        
    def getName(self):
        """return name of portType, or None
        """
        if self._portType.name:
            return self._portType.name
        else:
            return None

    def getOperationList(self):
        """returns list of operation objs
        """
        operations = []

        for op in self._portType.operations.values():
            operations.append(ZSIOperationAdapter(self._ws, op))
            
        return operations

class ZSIOperationAdapter(OperationInterface):
    """Inteface to operation class
    """
    def __init__(self, ws, op):
        OperationInterface.__init__(self, op)
        self._ws = ws
        
    def getName(self):
        """return name of operation, or None
        """
        if self._operation.name:
            return self._operation.name
        else:
            return None

    def getInput(self):
        """return input obj
        """
        return ZSIInputAdapter(self._ws, self._operation.input)

    def getOutput(self):
        """return output obj
        """
        return ZSIOutputAdapter(self._ws, self._operation.output)

    def getFaultList(self):
        """return list of fault objs
        """
        faults = []
        for fault in self._operation.faults.values():
            faults.append(ZSIFaultAdapter(fault))
        return faults

    def getExtensions(self):
        """return extensions
        """
        extensions = []

        for e in self._operation.extensions:
            extensions.append(ZSIExtensionFactory(e).getExtension())
        
        return extensions

    def getSoapBinding(self):
        """return op soap binding
        """
        sb = None
        
        for e in self.getExtensions():
            if isinstance(e, ZSISoapBindingAdapter):
                sb = e

        return sb


    def getSoapOperation(self):
        """return op soap operation
        """

        so = None

        for e in self.getExtensions():
            if isinstance(e, ZSISoapOperationAdapter):
                so = e
            elif isinstance(e, ZSISoapBodyAdapter):
                so = e

        return so

class ZSIFaultAdapter(FaultInterface):
    def getName(self):
        """fault name
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getMessage(self):
        """fault message
        """
        raise NotImplementedError, 'abstract method not implemented'

    def getExtensions(self):
        """return extensions
        """
        raise NotImplementedError, 'abstract method not implemented'

class ZSIInputAdapter(InputInterface):
    """Interface to input class
    """
    def __init__(self, ws, i):
        InputInterface.__init__(self, i)
        self._ws = ws
        
    def getMessage(self):
        """return message obj
        """
        return ZSIMessageAdapter(self._ws,
                                 self._ws.messages[self._input.message])

    def getExtensions(self):
        """return extensions
        """
        extensions = []
        
        for e in self._input.extensions:
            extensions.append(ZSIExtensionFactory(e).getExtension())
            
        return extensions

    def getSoapBody(self):
        """return input soap body
        """
        sb = None
        
        for e in self.getExtensions():
            if isinstance(e, ZSISoapBodyAdapter):
                sb = e

        return sb
    
class ZSIOutputAdapter(OutputInterface):
    """Inteface to output class
    """
    def __init__(self, ws, o):
        OutputInterface.__init__(self, o)
        self._ws = ws
        
    def getMessage(self):
        """return message obj
        """
        return ZSIMessageAdapter(self._ws,
                                 self._ws.messages[self._output.message])

    def getExtensions(self):
        """return extensions
        """
        extensions = []

        for e in self._output.extensions:
            extensions.append(ZSIExtensionFactory(e).getExtension())
        
        return extensions

class ZSIMessageAdapter(MessageInterface):
    """Inteface to message class
    """
    def __init__(self, ws, m):
        MessageInterface.__init__(self, m)
        self._ws = ws
        
    def getName(self):
        """return name of operation, or None
        """
        return (self._message.name or None)

    def getPartList(self):
        """return list of parts
        """
        parts = []
        for part in self._message.parts.values():
            parts.append(ZSIPartAdapter(self._ws, part))
        return parts

class ZSIPartAdapter(PartInterface):
    """Inteface to part class
    """
    def __init__(self, ws, p):
        PartInterface.__init__(self, p)
        self._ws = ws
        
    def getName(self):
        """return name of part, or None
        """
        return (self._part.name or None)

    def getElement(self):
        """return part's element or None
        """
        if self._part.element:
            return ZSITypeAdapter(self._ws, self._part.element)
        else:
            return None

    def getType(self):
        """return part's type or None
        """
        if self._part.type:
            return ZSITypeAdapter(self._ws, self._part.type)
        else:
            return None

class ZSITypeAdapter(TypeInterface):
    """Inteface to type class
    """
    def __init__(self, ws, t):
        TypeInterface.__init__(self, t)
        self._ws = ws
        
    def getName(self):
        """return name of type, or None
        """
        return self._type[1]

    def getTargetNamespace(self):
        """return targetnamespace of type
        """
        return self._type[0]

    def getQName(self):
        """return type's qname
        """
        return self._type[1]

    def isSimpleType(self):
        """Boolean - simple type?
        """
        # XXX: keep an eye on this

        if not self.isComplexType():
            return True
        else:
            return False
        
    def isComplexType(self):
        """Boolean - complex type?
        """
        
        iscomplex = False

        if self._ws.types.has_key( self.getTargetNamespace() ):
            if self._ws.types[self._type[0]].types.has_key(self._type[1]):
                if isinstance( self._ws.types[self._type[0]].\
                               types[self._type[1]],
                               ZSI.wstools.XMLSchema.ComplexType ):
                    iscomplex = True

        return iscomplex
        

    def isBasicElement(self):
        """Returns a type if is a primitive element type else None
        """
        
        pythontypes = {
            'int'   : 'types.IntType',
            'float' : 'types.FloatType',
            'str'   : 'types.StringType',
            'tuple' : 'types.TupleType',
            'list'  : 'types.ListType',
            }


        elementref = None

        if self._ws.types.has_key( self._type[0] ):
            if self._ws.types[self._type[0]].elements.has_key(self._type[1]):
                elementref = self._ws.types[self._type[0]].\
                             elements[self._type[1]]

        if elementref:
            if isinstance(elementref,
                          ZSI.wstools.XMLSchema.ElementDeclaration ):
                if elementref.attributes.has_key('type'):
                    bt = BaseTypeInterpreter()
                    ptype = bt.get_pythontype( elementref.\
                                               attributes['type'][1],
                                               elementref.\
                                               attributes['type'][0] )
                    if ptype:
                        return pythontypes[ptype]
                    else:
                        return False

        
        return False



class ZSIExtensionFactory(ExtensionFactory):
    """Extension Factory class
    """
    
    def getExtension(self):
        if isinstance(self._extObj, ZSI.wstools.WSDLTools.SoapAddressBinding ):
            return ZSISoapAddressAdapter( self._extObj )
        elif isinstance(self._extObj, ZSI.wstools.WSDLTools.SoapBinding ):
            return ZSISoapBindingAdapter( self._extObj )
        elif isinstance(self._extObj, ZSI.wstools.WSDLTools.\
                        SoapOperationBinding ):
            return ZSISoapOperationAdapter( self._extObj )
        elif isinstance(self._extObj, ZSI.wstools.WSDLTools.SoapBodyBinding ):
            return ZSISoapBodyAdapter( self._extObj )
        elif isinstance(self._extObj,
                        ZSI.wstools.WSDLTools.HttpAddressBinding ):
            # not currently handled
            pass
        elif isinstance( self._extObj, xml.dom.minidom.Element ):
            # XXX: wackyness in the xmlschema lib - blow it off
            pass
        else:
            # catch future needs
            raise WsdlInterfaceError, \
                  'extension factory failed for: %s' % self._extObj
        
class ZSISoapAddressAdapter(SoapAddressInterface):
    """Interface to soap address class
    """
    def getLocation(self):
        """Address location
        """
        return self._address.location

class ZSISoapBindingAdapter(SoapBindingInterface):
    """Interface to soap binding class
    """
    def getStyle(self):
        """Binding style
        """
        return self._binding.style

    def getTransport(self):
        """Binding transport
        """
        return self._binding.transport

class ZSISoapOperationAdapter(SoapOperationInterface):
    def getAction(self):
        """Operation action
        """
        return self._operation.soapAction

class ZSISoapBodyAdapter(SoapBodyInterface):
    """Interface to soap body class
    """
    def getUse(self):
        """Body use
        """
        return self._body.use

    def getNamespace(self):
        """Soap body namespace
        """
        return self._body.namespace

    def getEncoding(self):
        """Soap body encoding
        """
        return self._body.encodingStyle

###########################################################################
# Adapter classes for the XMLSchema/ZSI schema support
###########################################################################


class ZSISchemaAdapter(SchemaInterface):
    def getImports(self):
        """return list of imports
        """
        imports = []

        for i in self._schema.imports:
            imports.append( i.attributes['namespace'] )

        return imports
    
    def getTargetNamespace(self):
        """return targetnamespace of schema
        """
        return self._schema.targetNamespace

    def getXmlnsDict(self):
        """return xmlns dictionary
           {'prefix':'namespace', 'xmlns':'xmlns namespace'}
        """

        if self._schema.attributes.has_key('xmlns'):
            return self._schema.attributes['xmlns']
        else:
            return {}

    def getTypesDict(self):
        """return dictionary of all schema types
           {'name':type}
        """

        typesdict = {}

        if hasattr( self._schema, 'types' ):
            for k, v in self._schema.types.items():
                typesdict[k] = ZSISchemaTypeAdapter(v)

        return typesdict

    def getElementsDict(self):
        """return dictionary of all schema elements
           {'name':type}
        """
        
        elementdict = {}

        if hasattr( self._schema, 'elements' ):
            for k, v in self._schema.elements.items():
                elementdict[k] = ZSISchemaTypeAdapter(v)

        return elementdict


class ZSISchemaTypeAdapter(SchemaTypeInterface):
    """Adapter to schema types
    """
    def __adapterWrap(self, tp):

        if isinstance( tp, ZSI.wstools.XMLSchema.ComplexType ) or \
               isinstance( tp, ZSI.wstools.XMLSchema.SimpleType ):
            return ZSISchemaDefinitionAdapter(tp)
        elif isinstance( tp, ZSI.wstools.XMLSchema.ElementWildCard ):
             return ZSISchemaDeclarationAdapter(tp) # i think
        elif isinstance( tp, ZSI.wstools.XMLSchema.ElementDeclaration ) or \
                 isinstance( tp, ZSI.wstools.XMLSchema.\
                             LocalElementDeclaration ):
            if hasattr(tp, 'attributes') and tp.attributes.has_key('type'):
                if tp.getTypeDefinition('type'):
                    return self.__adapterWrap( tp.getTypeDefinition('type') )
                else:
                    # this is a hack, we have a primitive most likely
                    d = ZSISchemaDeclarationAdapter.DefinitionContainer()
                    d.attributes = self._type.attributes
                    return ZSISchemaDefinitionAdapter(d)
            elif hasattr(tp, 'content'):
                # a element containing a complex type
                if isinstance( tp.content,
                               ZSI.wstools.XMLSchema.LocalComplexType):
                    ctype = ZSISchemaDefinitionAdapter(tp.content)
                    #ctype._def.attributes['xsd'] = tp.attributes['xsd']
                    return ctype
                # otherwise...
                for c in tp.content:
                    if c.isDefinition():
                        return self.__adapterWrap(c)
            else:
                raise WsdlInterfaceError,\
                      'failed to handle element correctly'
        else:
            raise TypeError, 'unknown adapter type: %s' % tp

    def getName(self):
        """get the type name
        """

        if self._type.attributes.has_key('name'):
            return self._type.attributes['name']
        else:
            return None

    def getTargetNamespace(self):
        """get the ns
        """
        return self._type.getTargetNamespace()

    def getType(self):
        """get the type
        """
        if hasattr(self, '_type' ) and \
               self._type:
            return self.__adapterWrap( self._type )
        else:
            return None
    
    def isSimpleType(self):
        """boolean - simple type?
        """
        if isinstance(self._type, ZSI.wstools.XMLSchema.SimpleType):
            return True
        else:
            return False
                     
    def isComplexType(self):
        """boolean - complex type?
        """
        if isinstance(self._type, ZSI.wstools.XMLSchema.ComplexType):
            return True
        else:
            return False

    def isWildCard(self):
        """boolean - wild card declaration?
        """
        if isinstance(self._type, ZSI.wstools.XMLSchema.ElementWildCard):
            return True
        else:
            return False

    def isElement(self):
        """boolean - an element?
        """
        if isinstance(self._type, ZSI.wstools.XMLSchema.ElementDeclaration):
            return True
        else:
            return False

    def isLocalElement(self):
        """boolean - an element?
        """
        if isinstance(self._type, ZSI.wstools.XMLSchema.\
                      LocalElementDeclaration):
            return True
        else:
            return False

    def isAttribute(self):
        if isinstance(self._type, ZSI.wstools.XMLSchema.\
                      AttributeDeclaration) or \
                      isinstance(self._type, ZSI.wstools.XMLSchema.\
                                 AttributeGroupDefinition):
            return True
        else:
            return False
        
    def getDefinition(self):
        """return a SchemaDefinition object
        """
        return ZSISchemaDefinitionAdapter(self._type)

    def getDeclaration(self):
        """return a SchemaDeclaration object
        """
        return ZSISchemaDeclarationAdapter(self._type)


class ZSISchemaDefinitionAdapter(SchemaDefinitionInterface):

    def __adapterWrap(self, tp):
        if isinstance( tp, ZSI.wstools.XMLSchema.ComplexType ) or \
               isinstance( tp, ZSI.wstools.XMLSchema.SimpleType ):
            return ZSISchemaDefinitionAdapter(tp)
        elif isinstance( tp, ZSI.wstools.XMLSchema.ElementDeclaration ) or \
             isinstance( tp, ZSI.wstools.XMLSchema.ElementWildCard ) or \
             isinstance( tp, ZSI.wstools.XMLSchema.\
                         LocalElementDeclaration )or \
             isinstance(tp, ZSI.wstools.XMLSchema.\
                        LocalAttributeDeclaration) or \
             isinstance(tp, ZSI.wstools.XMLSchema.AttributeReference):
            return ZSISchemaDeclarationAdapter(tp)
        if isinstance( tp, ZSI.wstools.XMLSchema.ElementReference ):
            return self.__adapterWrap( tp.getElementDeclaration('ref') )
        else:
            raise TypeError, 'unknown adapter type: %s' % tp

    def isDefinition(self):
        return True

    def isDeclaration(self):
        return False
    
    def getTargetNamespace(self):
        """get NS
        """
        return self._def.getTargetNamespace()

    def getName(self):
        """get name
        """
        if self._def.attributes.has_key('name'):
            return self._def.attributes['name']
        else:
            return None

    def isComplexType(self):
        """boolean - complex type?
        """
        if isinstance(self._def, ZSI.wstools.XMLSchema.ComplexType) or \
               isinstance(self._def, ZSI.wstools.XMLSchema.LocalComplexType):
            return True
        else:
            return False

    def isComplexContent(self):
        """boolean - complex content type?
        """
        if isinstance(self._def.content, ZSI.wstools.XMLSchema.\
                      ComplexType.ComplexContent):
            return True
        else:
            return False

    def isSimpleContent(self):
        """boolean - simple content type?
        """
        if isinstance(self._def.content, ZSI.wstools.XMLSchema.\
                      ComplexType.SimpleContent):
            return True
        else:
            return False

    def getModelGroup(self):
        """returns a model group adapter
        """

        if self.isComplexType() and not self.isComplexContent():

            group = []

            if hasattr(self._def.content, 'content') and \
                   self._def.content.content:
                for c in self._def.content.content:
                    group.append( self.__adapterWrap( c ) )
                
            if isinstance( self._def.content,
                           ZSI.wstools.XMLSchema.All ):
                return ZSIModelGroupAdapter( group, all=True )
            elif isinstance( self._def.content,
                           ZSI.wstools.XMLSchema.Sequence ):
                return ZSIModelGroupAdapter( group, sequence=True )
            elif isinstance( self._def.content,
                           ZSI.wstools.XMLSchema.Choice ):
                return ZSIModelGroupAdapter( group, choice=True )
            else:
                # this is one of those goofy "void" cTypes
                return ZSIModelGroupAdapter( group )

            
        else:
            raise TypeError, 'complex type/non-complex content only'

    def getAttributes(self):
        # XXX: i think

        attr = []

        if hasattr( self._def, 'attr_content' ) and self._def.attr_content:
            for a in self._def.attr_content:
                attr.append( self.__adapterWrap(a) )

        return attr

    def getDerivedTypes(self):
        """returns derived type adapter
        """
        if isinstance( self._def.content, ZSI.wstools.XMLSchema.\
                       ComplexType.SimpleContent ):
            return ZSIDerivedTypesAdapter( self._def.content, simple=True )
        elif isinstance( self._def.content, ZSI.wstools.XMLSchema.\
                         ComplexType.ComplexContent ):
            return ZSIDerivedTypesAdapter( self._def.content, complex=True )
        else:
            raise WsdlInterfaceError, 'no derived type available'

    def isSimpleType(self):
        """boolean - simple type?
        """
        if isinstance(self._def, ZSI.wstools.XMLSchema.SimpleType) or \
               isinstance(self._def,
                          ZSISchemaDeclarationAdapter.DefinitionContainer):
            return True
        else:
            return False

    def getTypeclass(self):
        """get typeclass for simple type
        """

        if self.isSimpleType():
            tpc = None
            if hasattr(self._def, 'content') and \
                   isinstance(self._def.content, ZSI.wstools.XMLSchema.\
                              SimpleType.Restriction):
                bti = BaseTypeInterpreter()
                tpc = bti.get_typeclass( self._def.content.attributes['base'][1],
                                         self._def.content.attributes['base'][0])
            elif isinstance(self._def,
                            ZSISchemaDeclarationAdapter.DefinitionContainer):
                if not self._def.attributes.has_key('type'):
                    # ie: tpc = None
                    pass
                else:
                    bti = BaseTypeInterpreter()
                    tpc = bti.get_typeclass( self._def.attributes['type'][1],
                                             self._def.attributes['type'][0] )
            elif self._def.content:
                pass

            return tpc

        else:
            raise TypeError, 'simple type only'

    def getQName(self):
        """get qname for simple type
        """
        if self.isSimpleType():
            if self._def.attributes.has_key('type'):
                return self._def.attributes['type']
            else:
                raise WsdlInterfaceError, 'could not determine qname'
        else:
            raise TypeError, 'simple type only'

    def expressLocalAsGlobal(self, tp):
        """special case - for expressing a local complex type
        definition as a global one"""
        g = ZSISchemaDefinitionAdapter(self._def)
        g._def.attributes = tp._type.attributes.copy()
        g._def.attributes['name'] = g._def.attributes['name'] + 'LOCAL'
        return g


class ZSISchemaDeclarationAdapter(SchemaDeclarationInterface):

    class DefinitionContainer:
        def __init__(self):
            pass

    def __adapterWrap(self, tp):
        if isinstance( tp, ZSI.wstools.XMLSchema.ComplexType ) or \
               isinstance( tp, ZSI.wstools.XMLSchema.SimpleType ):
            return ZSISchemaDefinitionAdapter(tp)
        elif isinstance( tp, ZSI.wstools.XMLSchema.ElementDeclaration ) or \
                 isinstance( tp, ZSI.wstools.XMLSchema.ElementWildCard ) or \
                 isinstance( tp, ZSI.wstools.XMLSchema.\
                             LocalElementDeclaration ):
            return ZSISchemaDeclarationAdapter(tp)
        else:
            raise TypeError, 'unknown adapter type: %s' % tp

    def isDefinition(self):
        return False

    def isDeclaration(self):
        return True

    def isWildCard(self):
        """boolean - wild card declaration?
        """
        if isinstance(self._dec, ZSI.wstools.XMLSchema.ElementWildCard):
            return True
        else:
            return False

    def isAnyType(self):
        """boolean - any type dec?
        """
        # XXX: i think
        return self.isDefinition()

    def isElement(self):
        """boolean - an element?
        """
        if isinstance(self._dec, ZSI.wstools.XMLSchema.ElementDeclaration):
            return True
        else:
            return False

    def isLocalElement(self):
        """boolean - an element?
        """
        if isinstance(self._dec, ZSI.wstools.XMLSchema.\
                      LocalElementDeclaration):
            return True
        else:
            return False

    def getName(self):
        """returns name
        """
        if self._dec.attributes.has_key('name'):
            return self._dec.attributes['name']
        else:
            return None

    def getTargetNamespace(self):
        """return namespace
        """
        return self._dec.getTargetNamespace()

    def getType(self):
        """return type
        """
        if isinstance( self._dec, ZSI.wstools.XMLSchema.ElementReference ):
            return self.__adapterWrap( self._dec.getElementDeclaration('ref') )
        
        typ = self._dec.getTypeDefinition('type')

        if typ == None:
            d = ZSISchemaDeclarationAdapter.DefinitionContainer()
            d.attributes = self._dec.attributes
            return ZSISchemaDefinitionAdapter(d)
        else:
            return self.__adapterWrap( typ )
        

    def getMinOccurs(self):
        """min occurs in local element dec
        """
        if self._dec.attributes.has_key('minOccurs'):
            return self._dec.attributes['minOccurs']
        else:
            return 1

    def getMaxOccurs(self):
        """max occurs in local element dec
        """
        if self._dec.attributes.has_key('maxOccurs'):
            return self._dec.attributes['maxOccurs']
        else:
            return 1

    def isNillable(self):
        """see if an element is nillable
        """
        if self._dec.attributes.has_key('nillable'):
            return self._dec.attributes['nillable']
        else:
            return 0

class ZSIModelGroupAdapter(ModelGroupInterface):
    def isAll(self):
        """boolean - is complexType 'all'
        """
        return self._all

    def isChoice(self):
        """boolean - is complexType 'choice'
        """
        return self._choice

    def isSequence(self):
        """boolean - is complexType 'sequence'
        """
        return self._sequence

    def getContent(self):
        """return list of type data
        """
        return self._model

class ZSIDerivedTypesAdapter(DerivedTypesInterface):

    def isComplexContent(self):
        """boolean - is it complex content?
        """
        return self._complex

    def isSimpleContent(self):
        """boolean - is it simple content?
        """
        return self._simple

    def getArrayType(self):

        arrayinfo = None
        isDefined = None

        if hasattr(self._content, 'derivation'):
            if self._content.derivation.attr_content[0].attributes.\
                   has_key('arrayType'):
                t = self._content.derivation.attr_content[0].\
                    attributes['arrayType']

                if t[0:3] == 'xsd':
                    isDefined = False
                    tns = 'http://www.w3.org/2001/XMLSchema'
                    bti = BaseTypeInterpreter()
                    atype = bti.get_typeclass( t[4:-2], tns )
                else:
                    isDefined = True
                    ns, atype = SplitQName(t)
                    atype = atype[:-2]
                arrayinfo = ( t, atype, isDefined )

        else:
            raise WsdlInterfaceError, 'has no derivation base'
        
        if arrayinfo:
            return arrayinfo
        else:
            raise WsdlInterfaceError, 'could not determine array type'

    def getDerivation(self):

        # XXX: this will need more work

        derivation = None
        
        if hasattr(self._content, 'derivation'):
            if self._content.derivation.attributes.has_key('base'):
                derivation = self._content.derivation.attributes['base'][1]

        return derivation
        

    def getTypeclass(self):
        """get the typeclass of the derived type
        """

        if hasattr( self._content, 'derivation' ):
            if self._content.derivation.attributes.has_key('base'):
                bti = BaseTypeInterpreter()
                return bti.get_typeclass( self._content.derivation.\
                                          attributes['base'][1],
                                          self._content.derivation.\
                                          attributes['base'][0] )
            else:
                return None

                
        else:
            raise WsdlInterfaceError, 'derived type has no restriction base'

