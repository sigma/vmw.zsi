############################################################################
# Joshua Boverhof<JRBoverhof@lbl.gov>, LBNL
# Monte Goode <MMGoode@lbl.gov>, LBNL
# See Copyright for copyright notice!
############################################################################

import exceptions, sys, optparse, os, warnings, traceback
#from operator import xor
import ZSI
from ConfigParser import ConfigParser
from ZSI.generate.wsdl2python import WriteServiceModule, ServiceDescription as wsdl2pyServiceDescription
from ZSI.wstools import WSDLTools, XMLSchema
from ZSI.wstools.logging import setBasicLoggerDEBUG
from ZSI.generate import containers, utility
from ZSI.generate.utility import NCName_to_ClassName as NC_to_CN, TextProtect
from ZSI.generate.wsdl2dispatch import ServiceModuleWriter as ServiceDescription
from ZSI.generate.wsdl2dispatch import DelAuthServiceModuleWriter as DelAuthServiceDescription
from ZSI.generate.wsdl2dispatch import WSAServiceModuleWriter as ServiceDescriptionWSA
from ZSI.generate.wsdl2dispatch import DelAuthWSAServiceModuleWriter as DelAuthServiceDescriptionWSA

warnings.filterwarnings('ignore', '', exceptions.UserWarning)
def SetDebugCallback(option, opt, value, parser, *args, **kwargs):
    setBasicLoggerDEBUG()
    warnings.resetwarnings()

def SetPyclassMetaclass(option, opt, value, parser, *args, **kwargs):
    """set up pyclass metaclass for complexTypes"""
    from ZSI.generate.containers import ServiceHeaderContainer, TypecodeContainerBase, TypesHeaderContainer
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
    

def formatSchemaObject(fname, schemaObj):
    """ In the case of a 'schema only' generation (-s) this creates
        a fake wsdl object that will function w/in the adapters
        and allow the generator to do what it needs to do.
    """
    
    class fake:
        pass

    f = fake()

    if fname.rfind('/'):
        tmp = fname[fname.rfind('/') + 1 :].split('.')
    else:
        tmp = fname.split('.')

    f.name = '_'.join(tmp)
    f.types = { schemaObj.targetNamespace : schemaObj }

    return f

def wsdl2py(args=None):
    """Utility for automatically generating client/service interface code from a wsdl 
definition, and a set of classes representing element declarations and 
type definitions.  By default invoking this script produces three files, each 
named after the wsdl definition name, in the current working directory.
These files will end with '_client.py', '_types.py', '_server.py' 
respectively.                                                                    
    """
    op = optparse.OptionParser(usage="USAGE: %wsdl2py [options] WSDL",
                 description=wsdl2py.__doc__)
    
    # Basic options
    #op.add_option("-f", "--file",
    #              action="store", dest="file", default=None, type="string",
    #              help="FILE to load wsdl from")
    #op.add_option("-u", "--url",
    #              action="store", dest="url", default=None, type="string",
    #              help="URL to load wsdl from")
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
    
    # Extended generation options
    #op.add_option("-e", "--extended",
    #              action="store_true", dest="extended", default=False,
    #              help="Do Extended code generation.")    
    #op.add_option("-z", "--aname",
    #              action="store", dest="aname", default=None, type="string",
    #              help="pass in a function for attribute name creation")
    #op.add_option("-t", "--types",
    #              action="store", dest="types", default=None, type="string",
    #              help="file to load types from")
    op.add_option("-o", "--output-dir",
                  action="store", dest="output_dir", default=".", type="string",
                  help="save files in directory")
    op.add_option("-s", "--simple-naming",
                  action="store_true", dest="simple_naming", default=False,
                  help="map element names directly to python attributes")
    #op.add_option("-c", "--clientClassSuffix",
    #              action="store", dest="clientClassSuffix", default=None, type="string",
    #              help="Suffix to use for service client class (default \"SOAP\")")
    #op.add_option("-m", "--pyclassMapModule",
    #              action="store", dest="pyclassMapModule", default=None, type="string",
    #              help="Python file that maps external python classes to a schema type.  The classes are used as the \"pyclass\" for that type.  The module should contain a dict() called mapping in the format: mapping = {schemaTypeName:(moduleName.py,className) }")
                  
    if args is None:
        (options, args) = op.parse_args()
    else:
        (options, args) = op.parse_args(args)

    #if not xor(options.file is None, options.url is None):
    #    print 'Must specify either --file or --url option'
    #    sys.exit(os.EX_USAGE)
    #location = options.file            
    #if options.url is not None:
    #    location = options.url
    if len(args) != 1:
        print>>sys.stderr, 'Expecting a file/url as argument (WSDL).'
        sys.exit(os.EX_USAGE)
        
    location = args[0]
    
    if options.schema is True:
        reader = XMLSchema.SchemaReader(base_url=location)
    else:
        reader = WSDLTools.WSDLReader()

    load = reader.loadFromFile
    if not os.path.isfile(location):
        load = reader.loadFromURL

    wsdl = None
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

    modules = _wsdl2py(options, wsdl)
    modules.append(_wsdl2dispatch(options, wsdl))
    return modules
    
    
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

    #if options.clientClassSuffix:
    #    from ZSI.generate.containers import ServiceContainerBase
    #    ServiceContainerBase.clientClassSuffix = options.clientClassSuffix

    if options.schema is True:
        wsdl = formatSchemaObject(wsdl.location, wsdl)

    #if options.aname is not None:
    #    args = options.aname.rsplit('.',1)
    #    assert len(args) == 2, 'expecting module.function'
    #    # The following exec causes a syntax error.
    #    #exec('from %s import %s as FUNC' %(args[0],args[1]))
    #    assert callable(FUNC),\
    #        '%s must be a callable method with one string parameter' %options.aname
    #    from ZSI.generate.containers import TypecodeContainerBase
    #    TypecodeContainerBase.func_aname = staticmethod(FUNC)

    #if options.pyclassMapModule != None:
    #    mod = __import__(options.pyclassMapModule)
    #    components = options.pyclassMapModule.split('.')
    #    for comp in components[1:]:
    #        mod = getattr(mod, comp)
    #    extPyClasses = mod.mapping
    #else:
    #    extPyClasses = None
        
    #wsm = WriteServiceModule(wsdl, addressing=options.address, do_extended=options.extended, extPyClasses=extPyClasses)
    wsm = WriteServiceModule(wsdl, addressing=options.address)
#    if options.types != None:
#        wsm.setTypesModuleName(options.types)

    files = []
    append =  files.append
    if options.schema is False:
         client_mod = wsm.getClientModuleName()
         client_file = os.path.join(options.output_dir, '%s.py' %client_mod)
         append(client_file)
         fd = open(client_file, 'w+')

         # simple naming writes the messages to a separate file
         if not options.simple_naming:
             wsm.writeClient(fd)
         else: # provide a separate file to store messages to.
             msg_fd = open( os.path.join(options.output_dir, '%s.py' %wsm.getMessagesModuleName()), 'w+' )
             wsm.writeClient(fd, msg_fd=msg_fd)
             msg_fd.close()
         fd.close()

    
    types_mod = wsm.getTypesModuleName()
    types_file = os.path.join(options.output_dir, '%s.py' %types_mod)
    append(types_file)
    fd = open( os.path.join(options.output_dir, '%s.py' %types_mod), 'w+' )
    wsm.writeTypes(fd)
    fd.close()
    return files


def wsdl2dispatch(args=None):
    """
    wsdl2dispatch
    
    A utility for automatically generating service skeleton code from a wsdl
    definition.
    """
     
    op = optparse.OptionParser()
#    op.add_option("-f", "--file",
#                  action="store", dest="file", default=None, type="string",
#                  help="file to load wsdl from")
#    op.add_option("-u", "--url",
#                  action="store", dest="url", default=None, type="string",
#                  help="URL to load wsdl from")
    op.add_option("-a", "--address",
                  action="store_true", dest="address", default=False,
                  help="ws-addressing support, must include WS-Addressing schema.")
#    op.add_option("-e", "--extended",
#                  action="store_true", dest="extended", default=False,
#                  help="Extended code generation.")
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
    if os.path.isfile(args[0]):
        wsdl = reader.loadFromFile(args[0])
    else:
        wsdl = reader.loadFromURL(args[0])        

    return _wsdl2dispatch(options, wsdl)
    
    
def _wsdl2dispatch(options, wsdl):
    if options.simple_naming:
        ServiceDescription.server_module_suffix = '_interface'
        ServiceDescription.func_aname = lambda instnc,n: TextProtect(n)
        ServiceDescription.separate_messages = True
        # use module names rather than their number.
        utility.namespace_name = lambda cls, ns: utility.Namespace2ModuleName(ns)


    ss = None
    if options.address is True:
#        if options.extended:
#            ss = DelAuthServiceDescriptionWSA(do_extended=options.extended)
#        else:
            ss = ServiceDescriptionWSA()
    else:
#        if options.extended:
#            ss = DelAuthServiceDescription(do_extended=options.extended)
#        else:
            ss = ServiceDescription()

    ss.fromWSDL(wsdl)
    module_name = ss.getServiceModuleName()+'.py'
    fd = open( os.path.join(options.output_dir, module_name), 'w+')
    ss.write(fd)

    return module_name
    fd.close()
