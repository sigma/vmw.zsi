# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.

from ZSI import *
from ZSI.client import *
from ZSI.typeinterpreter import BaseTypeInterpreter
import wstools
from wstools.Utility import DOM
from urlparse import urlparse
import weakref

class ServiceProxy:
    """A ServiceProxy provides a convenient way to call a remote web
       service that is described with WSDL. The proxy exposes methods
       that reflect the methods of the remote web service."""

    def __init__(self, wsdl, service=None, port=None, tracefile=None,
                 typesmodule=None, nsdict=None, soapAction=None, ns=None, op_ns=None, use_wsdl=False):
        """
        Instance data
           use_wsdl -- if True try to construct XML Instance from 
                   information in WSDL.
        """
        if not hasattr(wsdl, 'targetNamespace'):
            wsdl = wstools.WSDLTools.WSDLReader().loadFromURL(wsdl)

#        for item in wsdl.types.items():
#            self._serializer.loadSchema(item)

        self._service = wsdl.services[service or 0]
        self.__doc__ = self._service.documentation
        self._port = self._service.ports[port or 0]
        self._name = self._service.name
        self._wsdl = wsdl
        self._tracefile = tracefile
        self._typesmodule = typesmodule
        self._nsdict = nsdict
        self._soapAction = soapAction
        self._ns = ns
        self._op_ns = op_ns
        self._use_wsdl = use_wsdl
        
        binding = self._port.getBinding()
        portType = binding.getPortType()
        for item in portType.operations:
            callinfo = wstools.WSDLTools.callInfoFromWSDL(self._port, item.name)
            method = MethodProxy(self, callinfo)
            setattr(self, item.name, method)

    def _call(self, name, *args, **kwargs):
        """Call the named remote web service method."""
        if len(args) and len(kwargs):
            raise TypeError(
                'Use positional or keyword argument only.'
                )

        callinfo = getattr(self, name).callinfo
        soapAction = callinfo.soapAction
        url = callinfo.location
        (protocol, host, uri, query, fragment, identifier) = urlparse(url)
        port = '80'
        if host.find(':') >= 0:
            host, port = host.split(':')

        binding = Binding(host=host, tracefile=self._tracefile,
                          ssl=(protocol == 'https'),
                          port=port, url=None, typesmodule=self._typesmodule,
                          nsdict=self._nsdict, soapaction=self._soapAction,
                          ns=self._ns, op_ns=self._op_ns)

        if self._use_wsdl:
            request, response = self._getTypeCodes(callinfo)
            if len(kwargs): args = kwargs
            binding.Send(url=uri, opname=None, obj=args,
                         nsdict=self._nsdict, soapaction=soapAction, requesttypecode=request)
            return binding.Receive(replytype=response)

        apply(getattr(binding, callinfo.methodName), args)

        return binding.Receive()

    def _getTypeCodes(self, callinfo):
        requestTC = self._getTypeCode(parameters=callinfo.getInParameters())
        replyTC = self._getTypeCode(parameters=callinfo.getOutParameters())

        if callinfo.style == 'rpc':
            request = TC.Struct(pyclass=None, ofwhat=requestTC, pname=callinfo.methodName)
            response = TC.Struct(pyclass=None, ofwhat=replyTC, pname='%sResponse' %callinfo.methodName)
        else:
            request = requestTC[0]
            response = replyTC[0]

        if callinfo.use == 'encoded':
            request.oname += ' xmlns="%s"' %callinfo.namespace

        return request, response

    def _getTypeCode(self, parameters):
        bti = BaseTypeInterpreter()
        typeCode = []
        for part in parameters:
            namespaceURI,localName = part.type

            if part.element_type:
                #global element
                element = self._wsdl.types[nsuri].elements[localName]
                name = element.attributes['name']
                tdc = element.attributes['element']
                typeClass = bti.get_typeclass(msg_type=tdc.getName(),
                                              targetNamespace=tdc.getTargetNamespace())
                tc = typeClass(name)
                if not typeClass:
                    element = self._wsdl.types[tdc.getTargetNamespace()].getElementDeclaration(tdc.getName())
                    tc = self._getElement(element)
                else:
                    tc = typeClass(name)

            else:
                #local element
                name = part.name
                typeClass = bti.get_typeclass(msg_type=localName, targetNamespace=namespaceURI)
                if not typeClass:
                    self._wsdl.types[namespaceURI].getTypeDefinition(localName)
                    typeClass = self._getElement()
                tc = typeClass(name)
            typeCode.append(tc)
        return typeCode

    def _getElement(self, element):
        name = element.getAttribute('name')
        tp = element.getTypeDefinition('type')
        if type(tp) in (types.StringType, types.Unicode):
            pass
        return self._getType(self, name, tp)
    
    def _getType(self, name, tp):
        return        


class MethodProxy:
    """ """
    def __init__(self, parent, callinfo):
        self.__name__ = callinfo.methodName
        self.__doc__ = callinfo.documentation
        self.callinfo = callinfo
        self.parent = weakref.ref(parent)

    def __call__(self, *args, **kwargs):
        return self.parent()._call(self.__name__, *args, **kwargs)
