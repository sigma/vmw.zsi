############################################################################
# Joshua Boverhof<JRBoverhof@lbl.gov>, LBNL
# Monte Goode <MMGoode@lbl.gov>, LBNL
# See Copyright for copyright notice!
############################################################################

import exceptions, sys, optparse, os, warnings, traceback
from os.path import isfile, join, split

#from operator import xor
import ZSI
from ConfigParser import ConfigParser
from ZSI.generate.wsdl2python import WriteServiceModule, ServiceDescription as wsdl2pyServiceDescription
from ZSI.wstools import WSDLTools, XMLSchema
from ZSI.wstools.logging import setBasicLoggerDEBUG
from ZSI.generate import containers, utility
from ZSI.generate.utility import NCName_to_ClassName as NC_to_CN, TextProtect
from ZSI.generate.wsdl2dispatch import ServiceModuleWriter as ServiceDescription
from ZSI.generate.wsdl2dispatch import WSAServiceModuleWriter as ServiceDescriptionWSA


warnings.filterwarnings('ignore', '', exceptions.UserWarning)
def SetDebugCallback(option, opt, value, parser, *args, **kwargs):
    setBasicLoggerDEBUG()
    warnings.resetwarnings()

def SetPyclassMetaclass(option, opt, value, parser, *args, **kwargs):
    """set up pyclass metaclass for complexTypes"""
    from ZSI.generate.containers import ServiceHeaderContainer,\
        TypecodeContainerBase, TypesHeaderContainer
        
    TypecodeContainerBase.metaclass = kwargs['metaclass']
    TypesHeaderContainer.imports.append(\
            'from %(module)s import %(metaclass)s' %kwargs
            )
    ServiceHeaderContainer.imports.append(\
            'from %(module)s import %(metaclass)s' %kwargs
            )

def SetUpTwistedClient(option, opt, value, parser, *args, **kwargs):
    from ZSI.generate.containers import ServiceHeaderContainer
    ServiceHeaderContainer.imports.remove('from ZSI import client')
    ServiceHeaderContainer.imports.append('from ZSI.twisted import client')
    
    
def SetUpLazyEvaluation(option, opt, value, parser, *args, **kwargs):
    from ZSI.generate.containers import TypecodeContainerBase
    TypecodeContainerBase.lazy = True
    


def wsdl2py(args=None):
    """Utility for automatically generating client/service interface code from
    a wsdl definition, and a set of classes representing element declarations 
    and type definitions.  By default invoking this script produces three files, 
    each named after the wsdl definition name, in the current working directory.
    
    Generated Modules Suffix:
        _client.py -- client locator, rpc proxy port, messages
        _types.py  -- typecodes representing 
        _server.py -- server-side bindings
        
    Parameters:
        args -- optional can provide arguments, rather than parsing 
            command-line.
            
    return:
        Default behavior is to return None, if args are provided then
        return names of the generated files.
                                                    
    """
    op = optparse.OptionParser(usage="USAGE: %wsdl2py [options] WSDL",
                 description=wsdl2py.__doc__)
    
    # Basic options
    op.add_option("-x", "--schema",
                  action="store_true", dest="schema", default=False,
                  help="process just the schema from an xsd file [no services]")

    op.add_option("-d", "--debug",
                  action="callback", callback=SetDebugCallback,
                  help="debug output")
                  
    # WS Options
    op.add_option("-a", "--address",
                  action="store_true", dest="address", default=False,
                  help="ws-addressing support, must include WS-Addressing schema.")
                  
    # pyclass Metaclass 
    op.add_option("-b", "--complexType",
                  action="callback", callback=SetPyclassMetaclass, 
                  callback_kwargs={'module':'ZSI.generate.pyclass', 
                      'metaclass':'pyclass_type'},
                  help="add convenience functions for complexTypes, including Getters, Setters, factory methods, and properties (via metaclass). *** DONT USE WITH --simple-naming ***")
    
    # Lazy Evaluation of Typecodes (done at serialization/parsing when needed).
    op.add_option("-l", "--lazy",
                  action="callback", callback=SetUpLazyEvaluation, 
                  callback_kwargs={},
                  help="EXPERIMENTAL: recursion error solution, lazy evalution of typecodes")
    
    # Use Twisted
    op.add_option("-w", "--twisted",
                  action="callback", callback=SetUpTwistedClient, 
                  callback_kwargs={'module':'ZSI.generate.pyclass', 
                      'metaclass':'pyclass_type'},
                  help="generate a twisted.web client/server, dependencies python>=2.4, Twisted>=2.0.0, TwistedWeb>=0.5.0")
    
    op.add_option("-o", "--output-dir",
                  action="store", dest="output_dir", default=".", type="string",
                  help="save files in directory")
    
    op.add_option("-s", "--simple-naming",
                  action="store_true", dest="simple_naming", default=False,
                  help="map element names directly to python attributes")
    
    is_cmdline = args is None
    if is_cmdline:
        (options, args) = op.parse_args()
    else:
        (options, args) = op.parse_args(args)

    if len(args) != 1:
        print>>sys.stderr, 'Expecting a file/url as argument (WSDL).'
        sys.exit(os.EX_USAGE)
        
    location = args[0]
    if options.schema is True:
        reader = XMLSchema.SchemaReader(base_url=location)
    else:
        reader = WSDLTools.WSDLReader()

    load = reader.loadFromFile
    if not isfile(location):
        load = reader.loadFromURL

    try:
        wsdl = load(location)
    except Exception, e:
        print >> sys.stderr, "Error loading %s: \n\t%s" % (location, e)
        traceback.print_exc(sys.stderr)
        # exit code UNIX specific, Windows?
        if hasattr(os, 'EX_NOINPUT'): sys.exit(os.EX_NOINPUT)
        sys.exit("error loading %s" %location)
  
    if isinstance(wsdl, XMLSchema.XMLSchema): 
        wsdl.location = location
        return _wsdl2py(options, wsdl)

    files = _wsdl2py(options, wsdl)
    files.append(_wsdl2dispatch(options, wsdl))
    if is_cmdline:
        return
    
    return files
    

def wsdl2dispatch(args=None):
    """Deprecated: wsdl2py now generates everything
    A utility for automatically generating service skeleton code from a wsdl
    definition.
    """
    op = optparse.OptionParser()
    op.add_option("-a", "--address",
                  action="store_true", dest="address", default=False,
                  help="ws-addressing support, must include WS-Addressing schema.")
    op.add_option("-d", "--debug",
                  action="callback", callback=SetDebugCallback,
                  help="debug output")
    op.add_option("-t", "--types",
                  action="store", dest="types", default=None, type="string",
                  help="Write generated files to OUTPUT_DIR")
    op.add_option("-o", "--output-dir",
                  action="store", dest="output_dir", default=".", type="string",
                  help="file to load types from")
    op.add_option("-s", "--simple-naming",
                  action="store_true", dest="simple_naming", default=False,
                  help="Simplify generated naming.")
    
    if args is None:
        (options, args) = op.parse_args()
    else:
        (options, args) = op.parse_args(args)
        
    if len(args) != 1:
        print>>sys.stderr, 'Expecting a file/url as argument (WSDL).'
        sys.exit(os.EX_USAGE)
        
    reader = WSDLTools.WSDLReader()
    if isfile(args[0]):
        _wsdl2dispatch(options, reader.loadFromFile(args[0]))
        return

    _wsdl2dispatch(options, reader.loadFromURL(args[0]))


def _wsdl2py(options, wsdl):
    if options.simple_naming:
        # Use a different client suffix
        # WriteServiceModule.client_module_suffix = "_client"
        # Write messages definitions to a separate file.
        #wsdl2pyServiceDescription.separate_messages = True
        # Use more simple type and element class names
        containers.SetTypeNameFunc( lambda n: '%s_' %(NC_to_CN(n)) )
        containers.SetElementNameFunc( lambda n: '%s' %(NC_to_CN(n)) )
        # Don't add "_" to the attribute name (remove when --aname works well)
        containers.ContainerBase.func_aname = lambda instnc,n: TextProtect(str(n))
        # write out the modules with their names rather than their number.
        utility.namespace_name = lambda cls, ns: utility.Namespace2ModuleName(ns)

    files = []
    append =  files.append
    if isinstance(wsdl, XMLSchema.XMLSchema):
        wsm = WriteServiceModule(_XMLSchemaAdapter(wsdl.location, wsdl),
                                 addressing=options.address)
    else:
        wsm = WriteServiceModule(wsdl, addressing=options.address)
        client_mod = wsm.getClientModuleName()
        client_file = join(options.output_dir, '%s.py' %client_mod)
        append(client_file)
        fd = open(client_file, 'w+')

        # simple naming writes the messages to a separate file
        if not options.simple_naming:
            wsm.writeClient(fd)
        else: # provide a separate file to store messages to.
            msg_fd = open(join(options.output_dir, 
                               '%s.py' %(wsm.getMessagesModuleName()), 'w+' ))
            wsm.writeClient(fd, msg_fd=msg_fd)
            msg_fd.close()
            
        fd.close()
    
    types_mod = wsm.getTypesModuleName()
    types_file = join(options.output_dir, '%s.py' %types_mod)
    append(types_file)
    fd = open( join(options.output_dir, '%s.py' %types_mod), 'w+' )
    wsm.writeTypes(fd)
    fd.close()
    
    return files


def _wsdl2dispatch(options, wsdl):
    if options.simple_naming:
        ServiceDescription.server_module_suffix = '_interface'
        ServiceDescription.func_aname = lambda instnc,n: TextProtect(n)
        ServiceDescription.separate_messages = True
        # use module names rather than their number.
        utility.namespace_name = lambda cls, ns: utility.Namespace2ModuleName(ns)

    if options.address is True:
        ss = ServiceDescriptionWSA()
    else:
        ss = ServiceDescription()

    ss.fromWSDL(wsdl)
    file_name = ss.getServiceModuleName()+'.py'
    fd = open( join(options.output_dir, file_name), 'w+')
    ss.write(fd)
    fd.close()
    
    return file_name


class _XMLSchemaAdapter:
    """Adapts an obj XMLSchema.XMLSchema to look like a WSDLTools.WSDL,
    just setting a couple attributes code expects to see.
    """
    def __init__(self, location, schema):
        """Parameters:
        location -- base location, file path
        schema -- XMLSchema instance
        """
        self.name = '_'.join(split(location)[-1].split('.'))
        self.types = {schema.targetNamespace:schema}
        

