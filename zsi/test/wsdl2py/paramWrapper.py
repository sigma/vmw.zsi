############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################

import sys, types
import ZSI

"""
paramWrapper:
    This is a utility module containing convenience functions for
    converting parameters and results involved with a ZSI remote
    method call to a string format suitable for printing.
"""

class TypecodeStrRep:
    """Builds up a type dictionary that can be used by sub-classes
       for building a string result.
    """

    def __init__(self, obj):
        self.stringBuf = ''
        self.typeDict = {}
        self.topObj = obj

            # namespace alias dictionary
        #self.nspAliases = {}
            # namespace handling class
        #self.nsh = ZSI.wsdl2python.NamespaceHash()

        self.recurseTypecodes(obj, self.typeDict)
        

    def getDictionary(self):
        return self.typeDict


    def getFullName(self, schema, aname):
        '''Get qualified name of element, with the namespace alias.
        '''

        name = self.nsh.namespace_to_moduleName(schema)
        qname = self.nspAliases[name] + '.' + aname 
        return qname


    def recurseTypecodes(self, obj, typedict):
        """Recursively generates list of parameter names and
           their values.
        """
        ofwhat = getattr(obj, 'ofwhat', None)
        if ofwhat:
            if type(ofwhat) is not types.TupleType:
                self.recurseTypecodes(ofwhat, typedict)
                return
            for item in ofwhat:
                schema = getattr(item, 'schema', None)
                optional = getattr(item, 'optional', None)
                tdict = {}
                self.recurseTypecodes(item, tdict)
                if schema:
                    typedict[item.aname] = [schema, item.__class__.__name__,
                                           optional, tdict]
                elif tdict.has_key('simple'):
                    typedict[item.aname] = [tdict['simple'],
                                           item.__class__.__name__,
                                           optional, 'simple']
                elif hasattr(item, 'ofwhat'):
                    typedict[item.aname] = [schema, item.__class__.__name__,
                                           optional, tdict]
        elif type(obj) is types.ListType:
            pass   # not handled yet
            #print 'typecodes list ', obj
        elif isinstance(obj, ZSI.TC.Struct):
            pass   # not handled yet
            #print 'typecodes struct ', obj.__class__
        elif isinstance(obj, ZSI.TC.TypeCode):
            if hasattr(obj, 'tag'):
                pythonType = obj.tag
            else:    # not the best, but for now ...
                pythonType = 'Any'
            typedict['simple'] = pythonType
        else:
            pass  # not handled yet
            #print 'typecodes not yet', obj


class ParamsToStr(TypecodeStrRep):

    def __init__(self, obj):
        TypecodeStrRep.__init__(self, obj)
        strList = ['\n']
        initStr = ''
        self.recurseBuildParams(self.typeDict, strList, initStr)
        self.stringBuf = ''.join(strList)

    def __str__(self):
        return self.stringBuf

    def recurseBuildParams(self, obj, strList, fieldStr):
        if type(obj) is types.DictType:
            for name, value in obj.items():
                appendStr = name + '.'
                self.recurseBuildParams(value, strList,
                                        fieldStr + appendStr)
        elif type(obj) is types.ListType:
            if type(obj[3]) is types.DictType:
                for name, value in obj[3].items():
                    appendStr = name + '.' 
                    self.recurseBuildParams(value, strList,
                                        fieldStr + appendStr)
            elif obj[3] == 'simple':
                if obj[2]:
                    strList.append('%s: %s, optional\n' % (fieldStr[:-1], obj[0]))
                else:
                    strList.append('%s: %s\n' % (fieldStr[:-1], obj[0]))


class ResultsToStr(TypecodeStrRep):

    def __init__(self, obj):
        TypecodeStrRep.__init__(self, obj)
        strList = ['\n']
        initStr = 'response.'
        self.recurseBuildResults(self.typeDict, strList, initStr)
        self.stringBuf = ''.join(strList)


    def __str__(self):
        return self.stringBuf


    def recurseBuildResults(self, obj, strList, fieldStr):
        if self.handleList(obj, strList, fieldStr):
            return
        if type(obj) is types.DictType:
            for name, value in obj.items():
                appendStr = name + '.'
                self.recurseBuildResults(value, strList, fieldStr + appendStr)
        elif type(obj) is types.ListType:
            if type(obj[3]) is types.DictType:
                for name, value in obj[3].items():
                    appendStr = name + '.' 
                    self.recurseBuildResults(value, strList, fieldStr + appendStr)
            elif obj[3] == 'simple':
                topIndex = len('response')
                realStr = 'self.topObj' + fieldStr[topIndex:-1]
                result = eval(realStr)
                strList.append('%s = %s\n' % (fieldStr[:-1], result))


    def handleList(self, obj, strList, fieldStr):
        topIndex = len('response')
        realStr = 'self.topObj' + fieldStr[topIndex:-1]
        result = eval(realStr)
        if result:
            if type(result) is types.ListType:
                ctr = 0
                fieldStr = fieldStr[:-1]
                for item in result:
                    appendStr = '[%d].' % (ctr)
                    self.recurseBuildResults(obj, strList, fieldStr + appendStr)
                    ctr += 1
                return True
            else:
                return False
        else:
            return True
