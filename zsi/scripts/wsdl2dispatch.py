#!/bin/env python

import ZSI, string, sys, getopt, urlparse
from ZSI.wstools import WSDLTools
from ZSI.wsdl2python import WriteServiceModule
from ZSI.wsdlInterface import ZSIWsdlAdapter


USAGE = """Usage: ./serverstub -f wsdlfile | -u url [-h]
  where:
    wsdl        -> wsdl file to generate callbacks from.
    -f          -> location of wsdl file in disc
    -x          -> enable experimental server code generation
    -u          -> location of wsdl via url
    -h          -> prints this message and exits.
"""

ID1 = '    '
ID2 = ID1 * 2
ID3 = ID1 * 3
ID4 = ID1 * 4


class ServerCallbackDescription:
    method_prefix = 'soap'

    def __init__(self):
        self.imports  = ''
        self.service  = ''
        self.classdef = ''
        self.initdef  = ''
        self.location = ''
        self.methods  = []
        self.actions  = []

    def fromWsdl(self, ws, do_extended = 0):

        wsm = ZSI.wsdl2python.WriteServiceModule(ws)

        self.service = wsm.get_module_names()[1]

        wsm = None

        ws = ZSIWsdlAdapter( ws )

        self.imports = self.getImports()

        for service in ws.getServicesList():
            for port in service.getPortList():
                # fetch the service location
                for e in port.getExtensions():
                    soapAddress = None
                    if isinstance(e, ZSI.wsdlInterface.ZSISoapAddressAdapter):
                        soapAddress = e
                    if soapAddress:
                        self.location = soapAddress.getLocation()
                # generate methods
                for op in port.getBinding().getPortType().getOperationList():
                    self.generateMethods(op, port, do_extended)
                    if do_extended:
                        self.generateMethods2(op, port)

        self.classdef = self.getClassdef(ws)
        self.initdef  = self.getInitdef(do_extended=do_extended)
        if do_extended:
            self.authdef = self.getAuthdef()
        else:
            self.authdef = ""

    def getImports(self):
        i  = 'from %s import *' % self.service
        i += '\nfrom ZSI.ServiceContainer import ServiceSOAPBinding'
        return i

    def getMethodName(self, method):
        return '%s_%s' %(self.method_prefix, method)

    def getClassdef(self, ws):
        c  = '\nclass %s(ServiceSOAPBinding):' \
             % ws.getName()
        c += '\n%ssoapAction = {' % ID1

        for a in self.actions:
            c += "\n%s'%s': '%s'," % (ID2, a[0], self.getMethodName(a[1]))
        
        c += '\n%s}' % ID2

        return c

    def getInitdef(self, do_extended=0):

        uri = urlparse.urlparse( self.location )[2]
        
        d  = "\n%sdef __init__(self, post='%s', **kw):" % (ID1, uri)
        d += '\n%sServiceSOAPBinding.__init__(self, post)' % ID2
        if do_extended:
            d += '\n%sif kw.has_key(\'impl\'):' % ID2
            d += '\n%sself.impl = kw[\'impl\']' % ID3

            d += '\n%sif kw.has_key(\'auth_method_name\'):' % ID2
            d += '\n%sself.auth_method_name = kw[\'auth_method_name\']' % ID3

        return d

    def getAuthdef(self):
        e = "\n%sdef authorize(self, auth_info, post, action):" % ID1
        e += "\n%sif self.auth_method_name and hasattr(self.impl, self.auth_method_name):" % ID2
        e += "\n%sreturn getattr(self.impl, self.auth_method_name)(auth_info, post, action)" % ID3
        e += "\n%selse:" % ID2
        e += "\n%sreturn 1" % ID3

        return e
    
    def generateMethods(self, op, port, do_extended=0):
        # generate soapactions while we're here
        operation = port.getBinding().getOperationDict().get(op.getName())

        if operation.getSoapOperation():
            action = operation.getSoapOperation().getAction()
            if action:
                self.actions.append( ( action, op.getName() ) )
            
        # now take care of the method
        o  = '\n%sdef %s(self, ps):' % (ID1, self.getMethodName(op.getName()))
        o += '\n%s# input vals in request object' % ID2
        o += '\n%sargs = ps.Parse( %s )' % ( ID2,
                            op.getInput().getMessage().getName() + 'Wrapper')

        o += '\n'
        
        
        if do_extended:
            input_args = op.getInput().getMessage().getPartList()
            iargs = ["%s" % x.getName() for x in input_args]
            iargs = ", ".join(iargs)
            for a in op.getInput().getMessage().getPartList():
                o += '\n%s# %s is a %s' % (ID2, a.getName(),
                                           a.getType().getName())
                o += '\n%s%s = args.%s' % (ID2, a.getName(), a.getName())
            o += "\n"
            
            invocation = '\n\n%s# Invoke the method' % ID2
            invocation += '\n%s%%sself.%s(%s)' % (ID2, op.getName(), iargs)

        if op.getOutput().getMessage() is not None:
            o += '\n%s# assign return values to response object' % ID2
            # JRB CHECK MESSAGE TO SEE IF ITS SIMPLE
            response_type = IsSimpleElementDeclaration(op, input=False)
            if response_type is False:
                o += '\n%sresponse = %s()' \
                     % ( ID2, op.getOutput().getMessage().getName() \
                         + 'Wrapper' )
            else:
                # can't instantiate a basestring, so by default do a str
                if response_type == 'basestring': response_type = 'str'
                o += '\n%sclass SimpleTypeWrapper(%s): typecode = %s()' \
                     % ( ID2,
                         response_type, op.getOutput().getMessage().getName()
                         + 'Wrapper' )
                o += '\n\n%s# WARNING specify value eg. SimpleTypeWrapper(1)' % ID2
                o += '\n%sresponse = SimpleTypeWrapper()'  % ID2

            if do_extended:
                output_args = op.getOutput().getMessage().getPartList()
                oargs = ["%s" % x.getName() for x in output_args]

                invoke_return = ""
                for ir in ["\n%sresponse.%s = %s" % (ID2, x.getName(), x.getName())
                           for x in output_args]:
                    invoke_return += ir

                    oargs = ", ".join(oargs)
                    if len(output_args) > 1:
                        print "Message has more than one return value (Bad Design)."
                        oargs = "(%s)" % oargs

                oargs = "%s = " % oargs

                o += invocation % oargs
                o += '\n'

                o += '\n%s# Assign return values to response' % ID2
                o += invoke_return
            
            o += '\n\n%s# Return the response' % ID2
            o += '\n%sreturn response' % ID2
        else:
            if do_extended:
                o += invocation % ""
                o += '\n'
            o += '\n%s# NO output' % ID2
            o += '\n%sreturn None' % ID2

        self.methods.append(o)

    def generateMethods2(self, op, port):
        # now take care of the method
        input_args = op.getInput().getMessage().getPartList()
        iargs = ["%s" % x.getName() for x in input_args]
        iargs = ", ".join(iargs)
        o  = '\n%sdef %s(self, %s):' % (ID1, op.getName(), iargs)
        for a in op.getInput().getMessage().getPartList():
            o += "\n%s# %s is a %s" % (ID2, a.getName(), a.getType().getName())

        o += "\n"

        if op.getOutput().getMessage():
            output_args = op.getOutput().getMessage().getPartList()
            oargs = ["%s" % x.getName() for x in output_args]
            oargs = ", ".join(oargs)
        else:
            output_args = None

        if output_args:
            if len(output_args) > 1:
                print "Message has more than one return value (Bad Design)."
                oargs = "(%s)" % oargs

            oargs = "%s = " % oargs

        else:
            oargs = ""

        o += "\n%s# If we have an implementation object use it" % ID2
        o += "\n%sif hasattr(self, 'impl'):" % ID2
        o += "\n%s%sself.impl.%s(%s)" % (ID3, oargs, op.getName(), iargs)
        o += "\n"
        
        if op.getOutput().getMessage() is not None:
            for a in op.getOutput().getMessage().getPartList():
                o += "\n%s# %s is a %s" % (ID2,
                                                            a.getName(),
                                                        a.getType().getName())
                o += "\n%sreturn %s" % (ID2, a.getName())

        else:
            o += "\n%s# There is no return from this method." % ID2

        self.methods.append(o)
        
    def getContents(self):
        gen_str = string.join([self.imports,
                               self.classdef,
                               self.initdef,
                               self.authdef,
                               string.join(self.methods, '\n')], '\n') + '\n'
        return gen_str

    def getStubName(self):
        return '%s_server' % self.service

    def write(self, fd=sys.stdout):
        fd.write( self.getContents() )


def IsSimpleElementDeclaration(op, input=True):

    prt = None
    if input is True and len( op.getInput().getMessage().getPartList() ) == 1:
        prt = op.getInput().getMessage().getPartList()[0]
    elif input is False and len( op.getOutput().getMessage().getPartList() ) == 1:
        prt = op.getOutput().getMessage().getPartList()[0]

    if prt is not None and prt.getElement():
        return prt.getElement().isBasicElement()
    return False


def doCommandLine():

    args_d = { 'fromfile': False, 'fromurl': False, 'extended' : False }
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'f:u:hx')
    except getopt.GetoptError, e:
        print >> sys.stderr, sys.argv[0] + ': ' + str(e)
        sys.exit(-1)

    if not opts:
        print USAGE
        sys.exit(-1)

    for opt, val in opts:
        if opt in [ '-h']:
            print USAGE
            sys.exit(0)
        elif opt in ['-f']:
            args_d['wsdl'] = val
            args_d['fromfile'] = True
        elif opt in ['-u']:
            args_d['wsdl'] = val
            args_d['fromurl'] = True
        elif opt in ['-x']:
            args_d['extended'] = True
        else:
            print USAGE
            sys.exit(-1)
            
    return args_d


def main():

    args_d = doCommandLine()

    reader = WSDLTools.WSDLReader()

    if args_d['fromfile']:
        wsdl = reader.loadFromFile(args_d['wsdl'])
    elif args_d['fromurl']:
        wsdl = reader.loadFromURL(args_d['wsdl'])

    ss = ServerCallbackDescription()

    ss.fromWsdl(wsdl, do_extended = args_d['extended'])

    fd = open( ss.getStubName() + '.py', 'w+' )

    ss.write(fd)

    fd.close()

if __name__ == '__main__':
    main()
