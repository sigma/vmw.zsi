test01 = '''<SOAP-ENV:Envelope foo='bar'
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
   <SOAP-ENV:Body>
       <m:GetLastTradePrice xmlns:m="Some-URI">
           <symbol>DIS</symbol>
       </m:GetLastTradePrice>
   </SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''

test02 = '''<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
   <!-- foo foo-pi -->
   <SOAP-ENV:Body>
       <m:GetLastTradePriceResponse xmlns:m="Some-URI">
           <Price>34.5</Price>
       </m:GetLastTradePriceResponse>
   </SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''

test03 = '''<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
<SOAP-ENV:Header>
   <t:Transaction xmlns:t="some-URI" SOAP-ENV:mustUnderstand="1">
          5
   </t:Transaction>
</SOAP-ENV:Header>
<SOAP-ENV:Body/>
</SOAP-ENV:Envelope>'''

test04 = '''<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
   <SOAP-ENV:Header>
       <t:Transaction
           actor="foobar"
           xmlns:t="some-URI"
           SOAP-ENV:mustUnderstand="1">
               5
       </t:Transaction>
   </SOAP-ENV:Header>
   <SOAP-ENV:Body>
       <m:GetLastTradePrice xmlns:m="Some-URI">
           <symbol>DEF</symbol>
       </m:GetLastTradePrice>
   </SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''

test05 = '''<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
   <SOAP-ENV:Body>
       <m:GetLastTradePriceDetailed
         xmlns:m="Some-URI">
           <Symbol>DEF</Symbol>
           <Company>DEF Corp</Company>
           <Price>34.1</Price>
       </m:GetLastTradePriceDetailed>
   </SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''

test06 = '''<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
  xmlns:xsi='xmlschemainstance'>
   <SOAP-ENV:Header>
       <t:Transaction xmlns:t="some-URI" xsi:type="xsd:int" mustUnderstand="1">
           5
           <nested mustUndertand="1"/>
       </t:Transaction>
   </SOAP-ENV:Header>
   <SOAP-ENV:Body>
       <m:GetLastTradePriceResponse xmlns:m="Some-URI">
           <m:Price>34.5</m:Price>
       </m:GetLastTradePriceResponse>
   </SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''

test07 = '''<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
   <SOAP-ENV:Body>
       <m:GetLastTradePriceResponse
         xmlns:m="Some-URI">
           <PriceAndVolume>
               <LastTradePrice>
                   34.5
               </LastTradePrice>
               <DayVolume>
                   10000
               </DayVolume>
           </PriceAndVolume>
       </m:GetLastTradePriceResponse>
   </SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''

test08 = '''<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
   <SOAP-ENV:Body>
       <SOAP-ENV:Fault>
           <faultcode>SOAP-ENV:MustUnderstand</faultcode>
           <faultstring>SOAP Must Understand Error</faultstring>
           <?MYPI spenser?>
       </SOAP-ENV:Fault>
   </SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''

test09 = '''<SOAP-ENV:Envelope fooattr='bar'
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
   <SOAP-ENV:Body>
       <SOAP-ENV:Fault>
           <faultcode>SOAP-ENV:Server</faultcode>
           <faultstring>Server Error</faultstring>
           <detail>
               <e:myfaultdetails xmlns:e="Some-URI">
                 <message>
                   My application didn't work
                 </message>
                 <errorcode>
                   1001
                 </errorcode>
               </e:myfaultdetails>
           </detail>
       </SOAP-ENV:Fault>
   </SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''

test10 = '''<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
   <SOAP-ENV:Body>
       <foo/>
       <m:GetLastTradePriceResponse xmlns:m="Some-URI">
           <Price>34.5</Price>
       </m:GetLastTradePriceResponse>
   </SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''

test11 = '''<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
   <SOAP-ENV:Body></SOAP-ENV:Body>
   <SOAP-ENV:Body></SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''

test12 = '''<SOAP-ENV:ChemicalX
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
   <SOAP-ENV:Body></SOAP-ENV:Body>
   <SOAP-ENV:Body></SOAP-ENV:Body>
</SOAP-ENV:ChemicalX>'''

test13 = '''<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
   <SOAP-ENV:Body></SOAP-ENV:Body>
   <SOAP-ENV:Header></SOAP-ENV:Header>
</SOAP-ENV:Envelope>'''

test14 = '''<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
   <SOAP-ENV:zBody></SOAP-ENV:zBody>
</SOAP-ENV:Envelope>'''

test15 = '''<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
   <SOAP-ENV:Header></SOAP-ENV:Header>
   <SOAP-ENV:Header></SOAP-ENV:Header>
   <SOAP-ENV:Body></SOAP-ENV:Body>
</SOAP-ENV:Envelope>'''

test16 = '''<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
   <SOAP-ENV:Header></SOAP-ENV:Header>
   <SOAP-ENV:Body></SOAP-ENV:Body>
   <SOAP-ENV:Header></SOAP-ENV:Header>
</SOAP-ENV:Envelope>'''

test17 = '''<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
   <SOAP-ENV:Header></SOAP-ENV:Header>
   <SOAP-ENV:Body></SOAP-ENV:Body>
   <m:data xmlns:m="data-URI">
       <symbol>DEF</symbol>
   </m:data>
</SOAP-ENV:Envelope>'''

test18 = '''<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
   <SOAP-ENV:Header></SOAP-ENV:Header>
   <SOAP-ENV:Body></SOAP-ENV:Body>
   <m:data xmlns:m="data-URI">
       <?PIE?>
       <symbol>DEF</symbol>
   </m:data>
</SOAP-ENV:Envelope>'''

test19 = '''<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
   <?xoo?>
   <SOAP-ENV:Header></SOAP-ENV:Header>
   <SOAP-ENV:Body></SOAP-ENV:Body>
   <m:data xmlns:m="data-URI">
       <symbol>DEF</symbol>
   </m:data>
</SOAP-ENV:Envelope>'''

