#!/bin/env python
############################################################################
# Joshua Boverhof<JRBoverhof@lbl.gov>, LBNL
# Monte Goode <MMGoode@lbl.gov>, LBNL
# See Copyright for copyright notice!
###########################################################################
import sys, optparse, os
from ZSI.wstools import WSDLTools
from ZSI.generate.wsdl2python import WriteServiceModule
from ZSI.generate.wsdl2dispatch import ServiceModuleWriter as ServiceDescription
from ZSI.generate.wsdl2dispatch import DelAuthServiceModuleWriter as DelAuthServiceDescription
from ZSI.generate.wsdl2dispatch import WSAServiceModuleWriter as ServiceDescriptionWSA
from ZSI.generate.wsdl2dispatch import DelAuthWSAServiceModuleWriter as DelAuthServiceDescriptionWSA
from ZSI.wstools.logging import setBasicLoggerDEBUG
from ZSI.generate.utility import TextProtect
from ZSI.generate import utility

"""
wsdl2dispatch

A utility for automatically generating service skeleton code from a wsdl
definition.
"""

def SetDebugCallback(option, opt, value, parser, *args, **kwargs):
    setBasicLoggerDEBUG()

def main():
    op = optparse.OptionParser()
    op.add_option("-f", "--file",
                  action="store", dest="file", default=None, type="string",
                  help="file to load wsdl from")
    op.add_option("-u", "--url",
                  action="store", dest="url", default=None, type="string",
                  help="URL to load wsdl from")
    op.add_option("-a", "--address",
                  action="store_true", dest="address", default=False,
                  help="ws-addressing support, must include WS-Addressing schema.")
    op.add_option("-e", "--extended",
                  action="store_true", dest="extended", default=False,
                  help="Extended code generation.")
    op.add_option("-d", "--debug",
                  action="callback", callback=SetDebugCallback,
                  help="debug output")
    op.add_option("-t", "--types",
                  action="store", dest="types", default=None, type="string",
                  help="file to load types from")
    op.add_option("-o", "--output-dir",
                  action="store", dest="output_directory", default=".", type="string",
                  help="file to load types from")
    op.add_option("-s", "--simple-naming",
                  action="store_true", dest="simple_naming", default=False,
                  help="Simplify generated naming.")
    (options, args) = op.parse_args()

    if options.simple_naming:
        ServiceDescription.server_module_suffix = '_interface'
        ServiceDescription.func_aname = lambda instnc,n: TextProtect(n)
        ServiceDescription.separate_messages = True
        # use module names rather than their number.
        utility.namespace_name = lambda cls, ns: utility.Namespace2ModuleName(ns)

    reader = WSDLTools.WSDLReader()
    wsdl = None
    if options.file is not None:
        wsdl = reader.loadFromFile(options.file)
    elif options.url is not None:
        wsdl = reader.loadFromURL(options.url)

    assert wsdl is not None, 'Must specify WSDL either with --file or --url'

    ss = None
    if options.address is True:
        if options.extended:
            ss = DelAuthServiceDescriptionWSA(do_extended=options.extended)
        else:
            ss = ServiceDescriptionWSA(do_extended=options.extended)
    else:
        if options.extended:
            ss = DelAuthServiceDescription(do_extended=options.extended)
        else:
            ss = ServiceDescription(do_extended=options.extended)

    ss.fromWSDL(wsdl)
    fd = open( os.path.join(options.output_directory, ss.getServiceModuleName()+'.py'), 'w+')
    ss.write(fd)
    fd.close()

if __name__ == '__main__':
    main()
