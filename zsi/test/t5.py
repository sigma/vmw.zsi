#! /usr/bin/env python
intext = '''Content-Type: multipart/mixed; boundary="sep"
Subject: testing

skip this

--sep
Content-type: text/xml

<foo xmlns='www.zolera.com'>hello world</foo>
--sep
Content-Type: text/plain
content-id: <part111@example.zolera.com>

this is some plain text
--sep
content-type: aplication/skipme

do not see this
okay?
--sep
Content-Type: text/xml
Content-ID: <part2@example.zolera.com>

<xml>spoken</xml>
--sep--
'''

import multifile, mimetools
import cStringIO as StringIO
from ZSI import resolvers
from xml.dom import Node
from xml.dom.ext.reader import PyExpat

istr = StringIO.StringIO(intext)
m = mimetools.Message(istr)
if  m.gettype()[0:10] == "multipart/":
    cid = resolvers.MIMEResolver(m['content-type'], istr)
    xml = cid.GetSOAPPart()
    print 'xml=', xml.getvalue()
    for h,b in cid.parts:
        print h, b.read()
    dom = PyExpat.Reader().fromStream(xml)
    print dom
