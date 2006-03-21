#! /usr/bin/env python
# $Header$
'''Typecodes for dates and times.
'''

from ZSI import _copyright, _floattypes, _inttypes, _get_idstr, EvaluateException
from ZSI.TC import TypeCode, SimpleType
from ZSI.wstools.Namespaces import SCHEMA
import operator, re, time

_niltime = [
    0, 0, 0,    # year month day
    0, 0, 0,    # hour minute second
    0, 0, 0     # weekday, julian day, dst flag
]

def _dict_to_tuple(d):
    '''Convert a dictionary to a time tuple.  Depends on key values in the
    regexp pattern!
    '''
    retval = _niltime[:]
    for k,i in ( ('Y', 0), ('M', 1), ('D', 2), ('h', 3), ('m', 4), ):
        v = d.get(k)
        if v: retval[i] = int(v)
    v = d.get('s')
    if v: retval[5] = int(float(v))
    v = d.get('tz')
    if v and v != 'Z':
        h,m = map(int, v.split(':'))
        if h < 0:
            retval[3] += abs(h)
            retval[4] += m
        else:
            retval[3] -= abs(h)
            retval[4] -= m
    if d.get('neg', 0):
        retval[0:5] = map(operator.__neg__, retval[0:5])
    return tuple(retval)



class Duration(SimpleType):
    '''Time duration.
    TODO: NOT FIXED YET...
    '''

    parselist = [ (None,'duration') ]
    lex_pattern = re.compile('^' r'(?P<neg>-?)P' \
                    r'((?P<Y>\d+)Y)?' r'((?P<M>\d+)M)?' r'((?P<D>\d+)D)?' \
                    r'(?P<T>T?)' r'((?P<h>\d+)H)?' r'((?P<m>\d+)M)?' \
                    r'((?P<s>\d*(\.\d+)?)S)?' '$')
    type = (SCHEMA.XSD3, 'duration')


    def text_to_data(self, text, elt, ps):
        '''convert text into typecode specific data.
        '''
        if text is None:
            return None
        m = Duration.lex_pattern.match(text)
        if m is None:
            raise EvaluateException('Illegal duration', ps.Backtrace(elt))
        d = m.groupdict()
        if d['T'] and (d['h'] is None and d['m'] is None and d['s'] is None):
            raise EvaluateException('Duration has T without time')
        try:
            retval = _dict_to_tuple(d)
        except ValueError, e:
            raise EvaluateException(str(e))
    
        if self.pyclass is not None:
            return self.pyclass(retval)
        return retval  
    
    def get_formatted_content(self, pyobj):
        if type(pyobj) in _floattypes or type(pyobj) in _inttypes:
            pyobj = time.gmtime(pyobj)
        
        d = {}
        pyobj = tuple(pyobj)
        if 1 in map(lambda x: x < 0, pyobj[0:6]):
            pyobj = map(abs, pyobj)
            neg = '-'
        else:
            neg = ''
            
        val = '%sP%dY%dM%dDT%dH%dM%dS' % \
            ( neg, pyobj[0], pyobj[1], pyobj[2], pyobj[3], pyobj[4], pyobj[5])

        return val
        

class Gregorian(SimpleType):
    '''Gregorian times.
    '''
    lex_pattern = tag = format = None

    def text_to_data(self, text, elt, ps):
        '''convert text into typecode specific data.
        '''
        if text is None:
            return None
        
        m = self.lex_pattern.match(text)
        if not m:
            raise EvaluateException('Bad Gregorian: %s' %text, ps.Backtrace(elt))
        try:
            retval = _dict_to_tuple(m.groupdict())
        except ValueError, e:
            raise EvaluateException(str(e))
        
        if self.pyclass is not None:
            return self.pyclass(retval)
        return retval    

#    def parse(self, elt, ps):
#        self.checkname(elt, ps)
#        elt = self.SimpleHREF(elt, ps, 'Gregorian')
#        if not elt: return None
#        if self.nilled(elt, ps): return Nilled
#        v = self.simple_value(elt, ps)
#        return self.text_to_data(text)

    def get_formatted_content(self, pyobj):
        if type(pyobj) in _floattypes or type(pyobj) in _inttypes:
            pyobj = time.gmtime(pyobj)
        
        d = {}
        pyobj = tuple(pyobj)
        if 1 in map(lambda x: x < 0, pyobj[0:6]):
            pyobj = map(abs, pyobj)
            d['neg'] = '-'
        else:
            d['neg'] = ''

        d = { 'Y': pyobj[0], 'M': pyobj[1], 'D': pyobj[2],
            'h': pyobj[3], 'm': pyobj[4], 's': pyobj[5], }
        val = self.format % d
        return val


class gDateTime(Gregorian):
    '''A date and time.
    '''
    parselist = [ (None,'dateTime') ]
    lex_pattern = re.compile('^' r'(?P<neg>-?)' \
                        '(?P<Y>\d{4,})-' r'(?P<M>\d\d)-' r'(?P<D>\d\d)' 'T' \
                        r'(?P<h>\d\d):' r'(?P<m>\d\d):' r'(?P<s>\d*(\.\d+)?)' \
                        r'(?P<tz>(Z|([-+]\d\d:\d\d))?)' '$')
    tag, format = 'dateTime', '%(Y)04d-%(M)02d-%(D)02dT%(h)02d:%(m)02d:%(s)02dZ'
    type = (SCHEMA.XSD3, 'dateTime')

class gDate(Gregorian):
    '''A date.
    '''
    parselist = [ (None,'date') ]
    lex_pattern = re.compile('^' r'(?P<neg>-?)' \
                        '(?P<Y>\d{4,})-' r'(?P<M>\d\d)-' r'(?P<D>\d\d)' \
                        r'(?P<tz>Z|([-+]\d\d:\d\d))?' '$')
    tag, format = 'date', '%(Y)04d-%(M)02d-%(D)02dZ'
    type = (SCHEMA.XSD3, 'date')

class gYearMonth(Gregorian):
    '''A date.
    '''
    parselist = [ (None,'gYearMonth') ]
    lex_pattern = re.compile('^' r'(?P<neg>-?)' \
                        '(?P<Y>\d{4,})-' r'(?P<M>\d\d)' \
                        r'(?P<tz>Z|([-+]\d\d:\d\d))?' '$')
    tag, format = 'gYearMonth', '%(Y)04d-%(M)02dZ'
    type = (SCHEMA.XSD3, 'gYearMonth')

class gYear(Gregorian):
    '''A date.
    '''
    parselist = [ (None,'gYear') ]
    lex_pattern = re.compile('^' r'(?P<neg>-?)' \
                        '(?P<Y>\d{4,})' \
                        r'(?P<tz>Z|([-+]\d\d:\d\d))?' '$')
    tag, format = 'gYear', '%(Y)04dZ'
    type = (SCHEMA.XSD3, 'gYear')

class gMonthDay(Gregorian):
    '''A gMonthDay.
    '''
    parselist = [ (None,'gMonthDay') ]
    lex_pattern = re.compile('^' r'(?P<neg>-?)' \
                        r'--(?P<M>\d\d)-' r'(?P<D>\d\d)' \
                        r'(?P<tz>Z|([-+]\d\d:\d\d))?' '$')
    tag, format = 'gMonthDay', '---%(M)02d-%(D)02dZ'
    type = (SCHEMA.XSD3, 'gMonthDay')


class gDay(Gregorian):
    '''A gDay.
    '''
    parselist = [ (None,'gDay') ]
    lex_pattern = re.compile('^' r'(?P<neg>-?)' \
                        r'---(?P<D>\d\d)' \
                        r'(?P<tz>Z|([-+]\d\d:\d\d))?' '$')
    tag, format = 'gDay', '---%(D)02dZ'
    type = (SCHEMA.XSD3, 'gDay')
    
class gMonth(Gregorian):
    '''A gMonth.
    '''
    parselist = [ (None,'gMonth') ]
    lex_pattern = re.compile('^' r'(?P<neg>-?)' \
                        r'---(?P<M>\d\d)' \
                        r'(?P<tz>Z|([-+]\d\d:\d\d))?' '$')
    tag, format = 'gMonth', '---%(M)02dZ'
    type = (SCHEMA.XSD3, 'gMonth')
    
class gTime(Gregorian):
    '''A time.
    '''
    parselist = [ (None,'time') ]
    lex_pattern = re.compile('^' r'(?P<neg>-?)' \
                        r'(?P<h>\d\d):' r'(?P<m>\d\d):' r'(?P<s>\d*(\.\d+)?)' \
                        r'(?P<tz>Z|([-+]\d\d:\d\d))?' '$')
    tag, format = 'time', '%(h)02d:%(m)02d:%(s)02dZ'
    type = (SCHEMA.XSD3, 'time')

if __name__ == '__main__': print _copyright
