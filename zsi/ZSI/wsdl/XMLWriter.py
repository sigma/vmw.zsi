# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.

from StringIO import StringIO
from Utility import DOM


class XMLWriter:
    """An XMLWriter provides a simplified interface for writing xml
       documents. The underlying DOM document may be accessed through
       the 'document' attribute of the writer. Note that the lifetime
       of the DOM document is bound to the lifetime of the writer."""

    def __init__(self, encoding='UTF-8'):
        self.encoding = encoding
        self.document = None
        self._stack = []
        self._nsmap = {}

    def __del__(self):
        if self.document is not None:
            self.document.unlink()
            self.document = None

    def startElement(self, name, namespaceURI=None, **attrs):
        """Begin a new element at the current point in the document."""
        tagname = self.makeQName(namespaceURI, name)
        if self.document is None:
            self.document = DOM.createDocument(namespaceURI, tagname)
            element = self.document.childNodes[0]
            self._stack.append(element)
            for name, value in attrs.items():
                self.writeAttr(name, value)
            return element
        if namespaceURI is not None:
            element = self.document.createElementNS(namespaceURI, tagname)
        else:
            element = self.document.createElement(tagname)
        stack = self._stack
        stack[-1].appendChild(element)
        stack.append(element)
        for name, value in attrs.items():
            self.writeAttr(name, value)
        return element

    def endElement(self):
        """End the last started element."""
        self._stack.pop()

    def currentElement(self):
        """Return the currently active DOM element of the writer."""
        return self._stack[-1]
        
    def writeAttr(self, name, value, namespaceURI=None):
        """Write an attribute to the current open element."""
        element = self._stack[-1]
        if namespaceURI is not None:
            attrname = self.makeQName(namespaceURI, name)
            element.setAttributeNS(namespaceURI, attrname, value)
        else:
            element.setAttribute(name, value)

    def writeText(self, value):
        """Write a string to the current element in the xml stream.
           Special characters in the given value will be escaped."""
        textnode = self.document.createTextNode(value)
        self._stack[-1].appendChild(textnode)

    def writeCDATA(self, value):
        """Write a CDATA section at the current point in the stream."""
        textnode = self.document.createCDATASection(value)
        self._stack[-1].appendChild(textnode)

    def writeXML(self, value):
        """Write a literal xml string to the stream. The data passed
           will not be escaped or modified on output."""
        textnode = LiteralText(value)
        textnode.ownerDocument = self.document
        self._stack[-1].appendChild(textnode)

    def declareNSDefault(self, namespaceURI):
        """Declare the default namespace uri to be used in the document."""
        if hasattr(self, '_nsdefault'):
            raise WriterError(
                'A default namespace is already set.'
                )
        self._nsdefault = namespaceURI
        self._nsmap[namespaceURI] = None

    def declareNSPrefix(self, prefix, namespaceURI):
        """Add an xml namespace prefix declaration to the document. All
           namespace declarations are written to the top level element."""
        if self._nsmap.has_key(namespaceURI):
            raise WriterError(
                'A prefix has already been declared for: %s' % namespaceURI
                )
        self._nsmap[namespaceURI] = prefix

    def hasNSPrefix(self, namespaceURI):
        """Return true if a prefix is declared for the given namespace uri."""
        return self._nsmap.has_key(namespaceURI)

    def getNSPrefix(self, namespaceURI):
        """Return the prefix to be used for the given namespace uri. A
           namespace prefix will be generated (and declared in the xml
           document) if a prefix for that uri has not been declared."""
        prefix = self._nsmap.get(namespaceURI, 0)
        if prefix is not 0:
            return prefix
        nsnum = getattr(self, '_nsnum', 0)
        self._nsnum = nsnum + 1
        prefix = 'ns%d' % nsnum
        self.declareNSPrefix(prefix, namespaceURI)
        return prefix

    def makeQName(self, namespaceURI, name):
        """Return an appropriate qname, given a name and namespace uri."""
        if namespaceURI is None:
            return name
        prefix = self.getNSPrefix(namespaceURI)
        if prefix is None: # default ns
            return name
        return '%s:%s' % (prefix, name)

    def makeRefId(self):
        """Return a generated unique id for use as an element reference."""
        idnum = getattr(self, '_idnum', 0)
        self._idnum = idnum + 1
        return 'ref-%d' % idnum

    def toString(self, format=0):
        """Return the xml stream as a string. If the format argument is
           a true value, the output will be formatted for readability."""
        if len(self._stack):
            tagname = self._stack[-1].tagName
            raise WriterError(
                'Missing endElement call for: %s' % tagname
                )

        element = self.document.childNodes[0]
        default = getattr(self, '_nsdefault', None)
        if default is not None:
            element.setAttribute('xmlns', default)
        for namespaceURI, prefix in self._nsmap.items():
            if prefix is not None:
                element.setAttribute('xmlns:%s' % prefix, namespaceURI)

        stream = StringIO()
        stream.write('<?xml version="1.0" encoding="%s"?>\n' % (
            self.encoding
            ))
        for child in self.document.childNodes:
            DOM.elementToStream(child, stream, format)
        return stream.getvalue()


from xml.dom.minidom import Text

class LiteralText(Text):
    def writexml(self, writer, indent="", addindent="", newl=""):
        writer.write("%s%s" % (self.data, newl))


class WriterError(Exception):
    pass
