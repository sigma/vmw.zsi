#! /usr/bin/env python

from ZSI import *
import sys
import tests

##  exceptions
def foo():
    '''dummy'''
    return 3 / 0

def bar():
    return foo() + 2

# Get the tests in numeric order.
results = []
for key,val in tests.__dict__.items():
    try:
        if key[0:4] == "test" and int(key[4:]) > 0: results.append((key,val))
    except:
        pass
results.sort(lambda a,b: cmp(a[0], b[0]))

if 1:
    class zParseException: pass
    for key,val in results:
        try:
            print "\n", "." * 60, key
            ps = ParsedSoap(val)
        except ParseException, e:
            print "SOAP ParseException:", e
            f = FaultFromZSIException(e)
            print f.AsSOAP()
            print `e`
            continue
        wmiu = ps.WhatMustIUnderstand()
        if len(wmiu): print "mustUnderstand", len(wmiu), wmiu
        actors = ps.WhatActorsArePresent()
        if len(actors): print "actors", len(actors), actors
        mine = ps.GetMyHeaderElements(['foobar', 'next'])
        if len(mine):
            print "mine", len(mine), \
                '[', ', '.join([m.nodeName for m in mine]), ']'

datatest = '''<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <SOAP-ENV:Header xmlns:t="http://www.zolera.com/ns/" xmlns:q='"'>
  <t:sometag SOAP-ENV:mustUnderstand="1">you must grok sometag</t:sometag>
  </SOAP-ENV:Header>
    <SOAP-ENV:Body xmlns='test-uri'>
        <root SOAP-ENC:root='1'/>
        <Price xsi:type='xsd:integer'>34</Price>        <!-- 0 -->
        <SOAP-ENC:byte>44</SOAP-ENC:byte>       <!-- 1 -->
        <Name>This is the name</Name>   <!-- 2 -->
        <n2><xmldoc><![CDATA[<greeting>Hello</greeting>]]></xmldoc></n2> <!-- 3 -->
        <n3 href='#zzz' xsi:type='SOAP-ENC:string'/>            <!-- 4 -->
        <n64>a GVsbG8=</n64>            <!-- 5 -->
        <SOAP-ENC:string>Red</SOAP-ENC:string>  <!-- 6 -->
        <a2 href='#tri2'/>              <!-- 7 -->
        <a2><i>12</i><t>rich salz</t></a2> <!-- 8 -->
        <xsd:hexBinary>3F2041</xsd:hexBinary> <!-- 9 -->
        <nullint xsi:nil='1'/> <!-- 10 -->
        <Anytest><urt-i xsi:type='SOAP-ENC:byte'>12</urt-i>
        <urt-t id="urtid"
                xsi:type="xsd:string">rich salz</urt-t></Anytest> <!-- 11 -->
        <uri>"http://foo.com/%7Esalz"</uri> <!-- 12 -->
        <floattest>             <!-- 13 -->
            <a>6.9</a> <b>-0</b> <c>INF</c>
        </floattest>
        <atest SOAP-ENC:offset='[3]' SOAP-ENC:arrayType="x">    <!-- 14 -->
            <i>12</i>
            <SOAP-ENC:integer id='n13'>13</SOAP-ENC:integer>
            <i>14</i>
            <i>15</i>
            <i>16</i>
            <i>17</i>
        </atest>
        <sarray SOAP-ENC:arrayType="struct"> <!-- 15 -->
            <i href="#zzz" xsi:type='xsd:string'/>
            <i href="#urtid"/>
            <thing href="#n13"/>
        </sarray>
        <xpath>//sarray</xpath> <!-- 16 -->
  <z xmlns='myns' xsi:type='SOAP-ENC:string' id='zzz'>The value of n3</z>
  <zz xmlns='myns2' id='tri2'><inner
  xmlns='myns2' ><f1>content</f1><sec xmlns='myns2'
  >ond</sec  ></inner></zz>
    </SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''

class myclass:
    def __init__(self, name):
        self.name = name or id(self)
        self.z = 'z value'
    def __str__(self):
        return 'myclass-%s-(%d,"%s")' % (self.name, self.i, self.t) + \
                str(self.z)

from xml.dom.ext.c14n import Canonicalize
ps = ParsedSoap(datatest)
#print ps.GetElementNSdict(ps.dom)
elts = ps.data_elements
print elts[10]

#print TC.IpositiveInteger(None).parse(elts[0], ps)
print 'opt int = ', TC.Integer(None, optional=1).parse(elts[10], ps)
print 'opt byte = ', TC.Ibyte(None, optional=1).parse(elts[10], ps)
#print 'non-opt int = ', TC.Integer(None, optional=0).parse(elts[10], ps)
B = [ TC.Integer('Price'), TC.Integer('p2'), TC.String(unique=1) ]
print TC.Integer(('test-uri', 'Price')).parse(elts[0], ps)
print B[0].parse(elts[0], ps)
print B[1].parse(elts[1], ps)
print B[2].parse(elts[2], ps)
print TC.HexBinaryString().parse(elts[9], ps)
print TC.String('Name').parse(elts[2], ps)
i = TC.Any('Price').parse(elts[0], ps)
print 'ur#1', type(i), i
i = TC.Any('n3').parse(elts[4], ps)
print 'ur#2', type(i), i
print TC.XML('n2').parse(elts[3], ps)
#nodelist = TC.XML('a2').parse(elts[7], ps)
#print 'n2="' + TC.String('n2').parse(elts[3], ps) + '"'
print TC.String('n3').parse(elts[4], ps)
print TC.Base64String('n64').parse(elts[5], ps)
print TC.String('n64').parse(elts[5], ps)
enum = TC.Enumeration(['Red', 'Blue', 'Green'], 'color')
print enum.parse(elts[6], ps)
#print TC.Integer('zzz').parse(elts[0], ps)

print 'enum=', TC.IEnumeration([44,46,47]).parse(elts[1],ps)
#S = TC.Struct(myclass, [TC.IunsignedShort('i'), TC.String('t')])
#print S.parse(elts[8], ps)
S = TC.Struct(None, [TC.String('t'), TC.Integer('i')], inorder=0)
pyobj = S.parse(elts[8], ps)
S2 = TC.Struct(myclass, [TC.IunsignedShort('i'), TC.String('q:z', optional=1), TC.String('t')], 'a2', typed=0)
pyobj2 = S2.parse(elts[8], ps)
print 'uri=', TC.URI().parse(elts[12], ps)
print pyobj == pyobj2, pyobj, pyobj2

tcary = TC.Array('SOAP-ENC:int', TC.Integer())
nsa = tcary.parse(elts[14],ps)
print 'non-sparse', nsa
tcary.sparse = 1
sa = tcary.parse(elts[14],ps)
print 'sparse', sa

mychoice = TC.Choice([
    TC.String('n3'),
    TC.URI('uri'),
    TC.Integer('Price'),
])

print '=' * 60
for i in [ 0, 12, 4 ] :
    b = mychoice.parse(elts[i], ps)
    print 'b=', type(b), b
print '=' * 60

print TC.Array('x', TC.Any()).parse(elts[15], ps)
print TC.Struct(None,
        (TC.FPfloat('a'), TC.Decimal('b'), TC.FPdouble('c'))).parse(elts[13],ps)
if 1:
    import sys, time
    nsdict = ps.GetElementNSdict(ps.header)
    nsdict[''] = "http://www.zolera.com/ns/"
    nsdict['q'] = 'q-namespace-uri'
    z = SoapWriter(sys.stdout, header=ps.header_elements, nsdict=nsdict)
    #pyobj2.z = 'z value!!'
    z.serialize(pyobj2, S2)
    S2.inline = 1
    S2.typed = 0
    #z.writeNSdict({'SOAP-ENV': 'foo'})
    tc = TC.gDateTime('dt')
    print '<!-- s2 -->'
    z.serialize(pyobj2, S2)
    z.serialize(pyobj, S)
    z.serialize(('n3', '******this is the value of a union'), mychoice)
    #z.serialize(nodelist, TC.XML('foo', nsdict=nsdict))
    z.serialize('uri:some/place/special', TC.XML('foo', nsdict=nsdict))
    tcary.sparse = 0
    z.serialize(nsa, tcary, childnames='tt')
    tcary.sparse = 1
    z.serialize(sa, tcary, name='MYSPARSEARRAY')
    z.serialize(time.time(), tc)
    z.serialize(time.time(), TC.gTime('monthday'))
    z.serialize('$$$$$foo<', TC.String(textprotect=0))
    z.close()
    print '|'+elts[11].getAttributeNS('foo','bar')+'|'
    print 'Any=', TC.Any().parse(elts[11], ps)
    #print 'Anydict2=', TC.Any().parse(elts[8], ps)

if 0:
    try:
        a = bar()
    except Exception, e:
        f = FaultFromException(e, 0, sys.exc_info()[2])
        print f.AsSOAP()
    print \
        FaultFromNotUnderstood('myuri', 'dalocalname', actor='cher').AsSOAP()
    FaultFromActor('actor:i:dont:understand').AsSOAP(sys.stdout)

sys.exit(0)
