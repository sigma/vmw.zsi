#!/usr/bin/env python
############################################################################
# David W. Robertson, LBNL
# See LBNLCopyright for copyright notice!
###########################################################################

import sys, types
import ZSI
from ZSI.typeinterpreter import BaseTypeInterpreter

"""
paramWrapper:
    This is a utility module containing convenience functions for
    dealing with parameters and results from a remote method call.
"""

RESULT_STR = 0
PARAMS_STR = 1
PARAMS_TREE = 2

class ParamWrapper:
    """Convenience class for handling parameters and results
       from a remote method call.
    """

    def __init__(self, obj, outputType=RESULT_STR):
        self.bti = BaseTypeInterpreter()
        self.isInput = False
        self.stringBuf = ''
        self.typeDict = {}
        self.topObj = obj

        self.recurseTypecodes(obj, self.typeDict)
        strList = ['\n']
        if outputType != PARAMS_TREE:
            if outputType == RESULT_STR:
                initStr = 'response.'
                self.recurseBuildResults(self.typeDict, strList, initStr)
            elif outputType == PARAMS_STR:
                initStr = ''
                self.recurseBuildParams(self.typeDict, strList, initStr)
            self.stringBuf = ''.join(strList)
        

    def __str__(self):
        return self.stringBuf


    def getDictionary(self):
        return self.typeDict


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
