#!/bin/env python
############################################################################
# Joshua Boverhof<JRBoverhof@lbl.gov>, LBNL
# Monte Goode <MMGoode@lbl.gov>, LBNL
# See Copyright for copyright notice!
###########################################################################
import sys, getopt
import ZSI
from ZSI.wsdl2python import WriteServiceModule
from ZSI.wstools import WSDLTools, XMLSchema

USAGE = """Usage: ./wsdl2py -f wsdl | -u url [-h] [-s] [-e] [-x] [-d outputdir] [-t typemodulename ]
  where:
    wsdl        -> wsdl file to generate typecodes from.
    -h          -> prints this message and exits.
    -f | -u     -> file or url to load wsdl from
    -e          -> enable experimental server code generation
    -x          -> process just the schema from an xsd file [no services]
    -z          -> specify a function to use to generate attribute names
    -d          -> output directory for files
    -t          -> specify a module name to use as the types implementation
"""

"""
wsdl2py

A utility for automatically generating client interface code from a wsdl
definition, and a set of classes representing element declarations and
type definitions.  This will produce two files in the current working 
directory named after the wsdl definition name.

eg. <definition name='SampleService'>
    SampleService.py
    SampleService_types.py

"""

def doCommandLine():
    """ Get command line options, print usage message if incorrect.
    """
    args_d = {
        'fromfile': False,
        'fromurl': False,
        'schemaOnly': False,
        'aname' : None,
        'output_directory' : '.',
        'extended' : False,
        'types' : None
        }
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'f:u:z:d:t:hxe')
    except getopt.GetoptError, e:
        print >>sys.stderr, sys.argv[0] + ': ' + str(e)
        sys.exit(-1)

    if not opts: 
        print USAGE
        sys.exit(-1)

    for opt, val in opts:
        if opt in [ '-h']:
            print USAGE
            sys.exit(0)
        elif opt in ['-e']:
            args_d['extended'] = True
        elif opt in ['-f']:
            args_d['wsdl'] = val
            args_d['fromfile'] = True
        elif opt in ['-u']:
            args_d['wsdl'] = val
            args_d['fromurl'] = True
        elif opt in ['-x']:
            args_d['schemaOnly'] = True
        elif opt in ['-z']:
            args_d['aname'] = val
        elif opt in ['-d']:
            args_d['output_directory'] = val
        elif opt in ['-t']:
            if val.endswith(".py"):
                args_d['types'] = val[:-3]
            else:
                args_d['types'] = val
        else:
            print USAGE
            sys.exit(-1)

    return args_d

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

    f.name  = tmp[0] + '_' + tmp[1]
    f.types = { schemaObj.targetNamespace : schemaObj }

    return f
    

def get_aname_func(aname):
    func = None

    args = aname.split('.')
    assert len(args) >= 2, 'expecting module.function'

    amod = ".".join(args[:-1])
    afunc = args[-1]

    try:
        exec('from %s import %s as FUNC' % (amod, afunc))
    except ImportError, e:
        e_str = "Specify a module.function to -z [%s]: " % aname
        print e_str, e
        return None
   
    assert callable(FUNC), '%s must be a callable method with one string parameter' % aname

    return FUNC

def main():
    """ From a wsdl definition create a wsdl object and run the wsdl2python 
        generator.  
    """
    args_d = doCommandLine()

    if args_d['aname']:
        aname_func = get_aname_func(args_d['aname'])
    else:
        aname_func = lambda x: "_%s" % x

    schemaOnly = args_d['schemaOnly']

    if schemaOnly:
        reader = XMLSchema.SchemaReader(base_url=args_d['wsdl'])
    else:
        reader = WSDLTools.WSDLReader()

    if args_d['fromfile']:
        wsdl = reader.loadFromFile(args_d['wsdl'])
    elif args_d['fromurl']:
        wsdl = reader.loadFromURL(args_d['wsdl'])

    if schemaOnly:
        wsdl = formatSchemaObject(args_d['wsdl'], wsdl)

    wsm = ZSI.wsdl2python.WriteServiceModule(wsdl, aname_func = aname_func)
    
    wsm.write(schemaOnly, output_dir=args_d['output_directory'],
              do_extended=args_d['extended'], types=args_d['types'])
    
    return

if __name__ == '__main__':
    main()
