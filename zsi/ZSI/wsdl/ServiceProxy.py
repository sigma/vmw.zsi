# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.

from SOAPCallInfo import callInfoFromWSDL
from WSDLTools import WSDLReader
from urlparse import urlparse
from ZSI import *
from ZSI.client import *
import weakref


class ServiceProxy:
    """A ServiceProxy provides a convenient way to call a remote web
       service that is described with WSDL. The proxy exposes methods
       that reflect the methods of the remote web service."""

    def __init__(self, wsdl, service=None, port=None):
        if not hasattr(wsdl, 'targetNamespace'):
            wsdl = WSDLReader().loadFromURL(wsdl)
#        for item in wsdl.types.items():
#            self._serializer.loadSchema(item)
        self._service = wsdl.services[service or 0]
        self.__doc__ = self._service.documentation
        self._port = self._service.ports[port or 0]
        self._name = self._service.name
        self._wsdl = wsdl
        binding = self._port.getBinding()
        portType = binding.getPortType()
        for item in portType.operations:
            callinfo = callInfoFromWSDL(self._port, item.name)
            method = MethodProxy(self, callinfo)
            setattr(self, item.name, method)

    def _call(self, name, *args, **kwargs):
        """Call the named remote web service method."""
        if len(args) and len(kwargs):
            raise TypeError(
                'Use positional or keyword argument only.'
                )

        callinfo = getattr(self, name).callinfo
        url = callinfo.location
        (protocol, host, uri, query, fragment, identifier) = urlparse(url)
        port = 80
        if host.find(':'):
            host, port = host.split(':')

        params = callinfo.getInParameters()
        host = str(host)
        port = str(port)
        binding = Binding(host=host, ssl=(protocol == 'https'),
                          port=port, url=uri)
        apply(getattr(binding, callinfo.methodName), '')

        #print binding.ReceiveRaw()

        return binding.Receive()


class MethodProxy:
    """ """
    def __init__(self, parent, callinfo):
        self.__name__ = callinfo.methodName
        self.__doc__ = callinfo.documentation
        self.callinfo = callinfo
        self.parent = weakref.ref(parent)

    def __call__(self, *args, **kwargs):
        return self.parent()._call(self.__name__, *args, **kwargs)
