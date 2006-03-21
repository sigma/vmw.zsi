#! /usr/bin/env python
# $Header$
'''Compound typecodes.
'''

from ZSI import _copyright, _children, _child_elements, \
    _inttypes, _stringtypes, _seqtypes, _find_arraytype, _find_href, \
    _find_type, _find_xmlns_prefix, _get_idstr, EvaluateException
from ZSI.TC import _get_element_nsuri_name, \
    _get_substitute_element, _get_type_definition, _get_xsitype, \
    TypeCode, Any, AnyElement, AnyType, ElementDeclaration, TypeDefinition, \
    Nilled
from ZSI.wstools.Namespaces import SCHEMA, SOAP
from ZSI.wstools.Utility import SplitQName
import re, types

_find_arrayoffset = lambda E: E.getAttributeNS(SOAP.ENC, "offset")
_find_arrayposition = lambda E: E.getAttributeNS(SOAP.ENC, "position")

_offset_pat = re.compile(r'\[[0-9]+\]')
_position_pat = _offset_pat

def _check_typecode_list(ofwhat, tcname):
    '''Check a list of typecodes for compliance with Struct
    requirements.'''
    for o in ofwhat:
        if not isinstance(o, TypeCode):
            raise TypeError(
                tcname + ' ofwhat outside the TypeCode hierarchy, ' +
                str(o.__class__))
        if o.pname is None and not isinstance(o, AnyElement):
            raise TypeError(tcname + ' element ' + str(o) + ' has no name')

def _is_derived_type(v, what):
    if isinstance(v, what.__class__):
        return True
    return False
 
def _get_what(v):
    if isinstance(v,TypeCode) is True:
        return v
    elif hasattr(v,'typecode') and isinstance(v,TypeCode):
        return typecode
    raise EvaluateException, 'instance is not self-describing'


def _set_element_from_type(v, what):
    if _is_derived_type(v,what):
        v.nspname = what.nspname
        v.pname = what.pname
        v.aname = what.aname
        v.minOccurs = what.minOccurs
        v.maxOccurs = what.maxOccurs
    else:
        raise EvaluateException, ''

def _get_any_instances(ofwhat, d):
    '''Run thru list ofwhat.anames and find unmatched keys in value
    dictionary d.  Assume these are element wildcard instances.  
    '''
    any_keys = []
    anames = map(lambda what: what.aname, ofwhat)
    for aname,pyobj in d.items():
        if isinstance(pyobj, AnyType) or aname in anames or pyobj is None:
            continue
        any_keys.append(aname)
    return any_keys


class ComplexType(TypeCode):
    '''Represents an element of complexType, potentially containing other elements.
    '''

    def __init__(self, pyclass, ofwhat, pname=None, inorder=False, inline=False,
    mutable=True, hasextras=0, mixed=False, mixed_aname='_text', **kw):
        '''pyclass -- the Python class to hold the fields
        ofwhat -- a list of fields to be in the struct
        hasextras -- ignore extra input fields
        inorder -- fields must be in exact order or not
        inline -- don't href/id when serializing
        mutable -- object could change between multiple serializations
        type -- the (URI,localname) of the datatype
        mixed -- mixed content model? True/False
        mixed_aname -- if mixed is True, specify text content here. Default _text
        '''
        TypeCode.__init__(self, pname, pyclass=pyclass, **kw)
        self.inorder = inorder
        self.inline = inline
        self.mutable = mutable
        self.mixed = mixed
        self.mixed_aname = None
        if mixed is True:
            self.mixed_aname = mixed_aname

        if self.mutable is True: self.inline = True
        self.hasextras = hasextras
        self.type = kw.get('type') or _get_xsitype(self)
        t = type(ofwhat)
        if t not in _seqtypes:
            raise TypeError(
                'Struct ofwhat must be list or sequence, not ' + str(t))
        self.ofwhat = tuple(ofwhat)
        if TypeCode.typechecks:
            # XXX Not sure how to determine if new-style class..
            if self.pyclass is not None and \
                type(self.pyclass) is not types.ClassType and not isinstance(self.pyclass, object):
                raise TypeError('pyclass must be None or an old-style/new-style class, not ' +
                        str(type(self.pyclass)))
            _check_typecode_list(self.ofwhat, 'ComplexType')

    def checktype(self, elt, ps):
        """If not exact type, check derived types.
        """
        checktype = TypeCode.checktype(self, elt, ps)
        return checktype

    def parse(self, elt, ps):
        self.checkname(elt, ps)
        if self.type and \
        self.checktype(elt, ps) not in [ self.type, (None,None) ]:
            raise EvaluateException('ComplexType for %s has wrong type(%s), looking for %s' %(
                self.pname, self.checktype(elt,ps), self.type), ps.Backtrace(elt))
        href = _find_href(elt)
        if href:
            if _children(elt):
                raise EvaluateException('Struct has content and HREF',
                        ps.Backtrace(elt))
            elt = ps.FindLocalHREF(href, elt)
        c = _child_elements(elt)
        count = len(c)
        if self.nilled(elt, ps): return Nilled
        repeatable_args = False
        for tc in self.ofwhat:
            if tc.maxOccurs > 1:
                repeatable_args = True
                break

        if not repeatable_args:
            if count > len(self.ofwhat) and not self.hasextras:
                raise EvaluateException('Too many sub-elements (%d>%d)' %(
                    count,len(self.ofwhat)), ps.Backtrace(elt))

        # Create the object.
        v = {}

        # parse all attributes contained in attribute_typecode_dict (user-defined attributes),
        # the values (if not None) will be keyed in self.attributes dictionary.
        attributes = self.parse_attributes(elt, ps)
        if attributes:
            v[self.attrs_aname] = attributes

        #MIXED
        if self.mixed is True:
            v[self.mixed_aname] = self.simple_value(elt,ps)

        # Clone list of kids (we null it out as we process)
        c, crange = c[:], range(len(c))
        # Loop over all items we're expecting
        self.logger.debug("OFWHAT: %s",str(self.ofwhat))
        any = None
        for i,what in [ (i, self.ofwhat[i]) for i in range(len(self.ofwhat)) ]:
            # Loop over all available kids
            self.logger.debug("WHAT: (%s,%s)", what.nspname, what.pname)
            for j,c_elt in [ (j, c[j]) for j in crange if c[j] ]:
                self.logger.debug("C_ELT: (%s,%s)", c_elt.namespaceURI, c_elt.tagName)
                if what.name_match(c_elt):
                    # Parse value, and mark this one done. 
                    try:
                        value = what.parse(c_elt, ps)
                    except EvaluateException, e:
                        #what = _get_substitute_element(c_elt, what)
                        #value = what.parse(c_elt, ps)
                        raise
                    if what.maxOccurs > 1:
                        if v.has_key(what.aname):
                            v[what.aname].append(value)
                        else:
                            v[what.aname] = [value]
                        c[j] = None
                        continue
                    else:
                        v[what.aname] = value
                    c[j] = None
                    break
                else:
                    self.logger.debug("==> DIDNT FIND: element(%s,%s)",what.nspname,what.pname)

                # No match; if it was supposed to be here, that's an error.
                if self.inorder is True and i == j:
                    raise EvaluateException('Out of order struct',
                            ps.Backtrace(c_elt))
            else:
                # only supporting 1 <any> declaration in content.
                if isinstance(what,AnyElement):
                    any = what
                elif hasattr(what, 'default'):
                    v[what.aname] = what.default
                elif what.minOccurs > 0 and not v.has_key(what.aname):
                    raise EvaluateException('Element "' + what.aname + \
                        '" missing from struct', ps.Backtrace(elt))

        # Look for wildcards and unprocessed children
        # XXX Stick all this stuff in "any", hope for no collisions
        if any is not None:
            occurs = 0
            v[any.aname] = []
            for j,c_elt in [ (j, c[j]) for j in crange if c[j] ]:
                value = any.parse(c_elt, ps)
                if any.maxOccurs == 'unbounded' or any.maxOccurs > 1:
                    v[any.aname].append(value)
                else:
                    v[any.aname] = value

                occurs += 1

            # No such thing as nillable <any>
            if any.maxOccurs == 1 and occurs == 0:
                v[any.aname] = None
            elif occurs < any.minOccurs or (any.maxOccurs!='unbounded' and any.maxOccurs<occurs):
                raise EvaluateException('occurances of <any> elements(#%d) bound by (%d,%s)' %(
                    occurs, any.minOccurs,str(any.maxOccurs)), ps.Backtrace(elt))

        if not self.pyclass: 
            return v

        # type definition must be informed of element tag (nspname,pname),
        # element declaration is initialized with a tag.
        try:
            if issubclass(self.pyclass, ElementDeclaration) is False and\
               issubclass(self.pyclass, TypeDefinition) is True:
                pyobj = self.pyclass((self.nspname,self.pname))
            else:
                pyobj = self.pyclass()
        except Exception, e:
            raise TypeError("Constructing element (%s,%s) with pyclass(%s), %s" \
                %(self.nspname, self.pname, self.pyclass.__name__, str(e)))
        for key in v.keys():
            setattr(pyobj, key, v[key])
        return pyobj

    def serialize(self, elt, sw, pyobj, inline=False, name=None, **kw):
        if inline or self.inline:
            self.cb(elt, sw, pyobj, **kw)
        else:
            objid = _get_idstr(pyobj)
            n = name or self.pname or ('E' + objid)
            el = elt.createAppendElement(None, n)
            el.setAttributeNS(None, 'href', "#%s" %objid)
            sw.AddCallback(self.cb, elt, sw, pyobj)

    def cb(self, elt, sw, pyobj, name=None, **kw):
        self.logger.debug("SERIALIZE OFWHAT: %s",str(self.ofwhat))
        if pyobj is None:
            if self.nillable is True:
                elem = elt.createAppendElement(self.nspname, self.pname)
                self.serialize_as_nil(elem)
                return
            raise EvaluateException, 'element(%s,%s) is not nillable(%s)' %(
                self.nspname,self.pname,self.nillable)

        if self.mutable is False and sw.Known(pyobj): 
            return
        
        objid = _get_idstr(pyobj)
        #n = name or self.pname or ('E' + objid)
        n = name or self.pname
        self.logger.debug("TAG: (%s, %s)", str(self.nspname), n)
        if n is not None:
            elem = elt.createAppendElement(self.nspname, n)
            self.set_attributes(elem, pyobj)
            if kw.get('typed', self.typed) is True:
                self.set_attribute_xsi_type(elem)

            #MIXED For now just stick it in front.
            if self.mixed is True and self.mixed_aname is not None:
               if hasattr(pyobj, self.mixed_aname):
                   textContent = getattr(pyobj, self.mixed_aname)
                   if hasattr(textContent, 'typecode'):
                       textContent.typecode.serialize_text_node(elem, sw, textContent)
                   elif type(textContent) in _stringtypes:
                       self.logger.debug("mixed text content:\n\t%s", textContent)
                       elem.createAppendTextNode(textContent)
                   else:
                       raise EvaluateException('mixed test content in element (%s,%s) must be a string type' %(
                           self.nspname,self.pname), sw.Backtrace(elt))
               else:
                   self.logger.debug("mixed NO text content in %s", self.mixed_aname)
        else:
            #For information items w/o tagNames 
            #  ie. model groups,SOAP-ENC:Header
            elem = elt

        if self.inline:
            pass
        elif not self.inline and self.unique:
            raise EvaluateException('Not inline, but unique makes no sense. No href/id.',
                sw.Backtrace(elt))
        elif n is not None:
            self.set_attribute_id(elem, objid)

        if self.pyclass:
            d = pyobj.__dict__
        else:
            d = pyobj
            if TypeCode.typechecks and type(d) != types.DictType:
                raise TypeError("Classless struct didn't get dictionary")

        indx, lenofwhat = 0, len(self.ofwhat)
        self.logger.debug('element declaration (%s,%s)', self.nspname, self.pname)
        if self.type:
            self.logger.debug('xsi:type definition (%s,%s)', self.type[0], self.type[1])
        else:
            self.logger.warning('NO xsi:type')

        while indx < lenofwhat:
            occurs = 0
            what = self.ofwhat[indx]
            self.logger.debug('serialize what -- %s', what.__class__.__name__)

            # No way to order <any> instances, so just grab any unmatched
            # anames and serialize them.  Only support one <any> in all content.
            # Must be self-describing instances

            # Regular handling of declared elements
            aname = what.aname
            v = d.get(aname)
            indx += 1
            if what.minOccurs == 0 and v is None: 
                continue

            # Default to typecode, if self-describing instance, and check 
            # to make sure it is derived from what.
            whatTC = what
            if _is_derived_type(v, whatTC):
                what = _get_what(v)
                _set_element_from_type(what, whatTC)

            if whatTC.maxOccurs > 1 and v is not None:
                if type(v) not in _seqtypes:
                    raise EvaluateException('pyobj (%s,%s), aname "%s": maxOccurs %s, expecting a %s' %(
                         self.nspname,self.pname,what.aname,whatTC.maxOccurs,_seqtypes), 
                         sw.Backtrace(elt))

                for v2 in v: 
                    occurs += 1
                    if occurs > whatTC.maxOccurs:
                        raise EvaluateException('occurances (%d) exceeded maxOccurs(%d) for <%s>' %(
                                occurs, whatTC.maxOccurs, what.pname), 
                                sw.Backtrace(elt))
                    try:
                        what.serialize(elem, sw, v2, **kw)
                    except Exception, e:
                        raise EvaluateException('Serializing %s.%s, %s %s' %
                            (n, whatTC.aname or '?', e.__class__.__name__, str(e)))

                if occurs < whatTC.minOccurs:
                    raise EvaluateException('occurances(%d) less than minOccurs(%d) for <%s>' %(
                            occurs, whatTC.minOccurs, what.pname), sw.Backtrace(elt))
                continue

            if v is not None or what.nillable is True:
                try:
                    what.serialize(elem, sw, v, **kw)
                except Exception, e:
                    raise EvaluateException('Serializing %s.%s, %s %s' %
                        (n, whatTC.aname or '?', e.__class__.__name__, str(e)),
                        sw.Backtrace(elt))
                continue

            raise EvaluateException('Got None for nillable(%s), minOccurs(%d) element (%s,%s), %s' %
                    (what.nillable, what.minOccurs, what.nspname, what.pname, elem),
                    sw.Backtrace(elt))


    def setDerivedTypeContents(self, extensions=None, restrictions=None):
        """For derived types set appropriate parameter and 
        """
        if extensions:
            ofwhat = list(self.ofwhat)
            if type(extensions) in _seqtypes:
                ofwhat += list(extensions)
            else:
                ofwhat.append(extensions)
        elif restrictions:
            if type(restrictions) in _seqtypes:
                ofwhat = restrictions
            else:
                ofwhat = (restrictions,)
        else:
            return
        self.ofwhat = tuple(ofwhat)
        self.lenofwhat = len(self.ofwhat)


class Struct(ComplexType):
    '''Struct is a complex type for accessors identified by name. 
       Constraint: No element may be have the same name as any other,
       nor may any element have a maxOccurs > 1.
       
      <xs:group name="Struct" >
        <xs:sequence>
          <xs:any namespace="##any" minOccurs="0" maxOccurs="unbounded" processContents="lax" />
        </xs:sequence>
      </xs:group>

      <xs:complexType name="Struct" >
        <xs:group ref="tns:Struct" minOccurs="0" />
        <xs:attributeGroup ref="tns:commonAttributes"/>
      </xs:complexType> 
    '''

    def __init__(self, pyclass, ofwhat, pname=None, inorder=False, inline=False,
        mutable=True, hasextras=0, **kw):
        '''pyclass -- the Python class to hold the fields
        ofwhat -- a list of fields to be in the struct
        hasextras -- ignore extra input fields
        inorder -- fields must be in exact order or not
        inline -- don't href/id when serializing
        mutable -- object could change between multiple serializations
        '''
        ComplexType.__init__(self, pyclass, ofwhat, pname=pname, 
            inorder=inorder, inline=inline, mutable=mutable, 
            hasextras=hasextras, **kw
            )
        
        # Check Constraints
        whats = map(lambda what: (what.nspname,what.pname), self.ofwhat)
        for idx in range(len(self.ofwhat)):
            what = self.ofwhat[idx]
            key = (what.nspname,what.pname)
            if not isinstance(what, AnyElement) and what.maxOccurs > 1:
                raise TypeError,\
                    'Constraint: no element can have a maxOccurs>1'
            if key in whats[idx+1:]:
                raise TypeError,\
                    'Constraint: No element may have the same name as any other'


class Array(TypeCode):
    '''An array.
        atype -- arrayType, (namespace,ncname) 
        mutable -- object could change between multiple serializations
        undeclared -- do not serialize/parse arrayType attribute.
    '''

    def __init__(self, atype, ofwhat, pname=None, dimensions=1, fill=None,
    sparse=False, mutable=False, size=None, nooffset=0, undeclared=False,
    childnames=None, **kw):
        TypeCode.__init__(self, pname, **kw)
        self.dimensions = dimensions
        self.atype = atype
        if undeclared is False and self.atype[1].endswith(']') is False:
            self.atype = (self.atype[0], '%s[]' %self.atype[1])
        # Support multiple dimensions
        if self.dimensions != 1:
            raise TypeError("Only single-dimensioned arrays supported")
        self.fill = fill
        self.sparse = sparse
        if self.sparse: ofwhat.optional = 1
        self.mutable = mutable
        self.size = size
        self.nooffset = nooffset
        self.undeclared = undeclared
        self.childnames = childnames
        if self.size:
            t = type(self.size)
            if t in _inttypes:
                self.size = (self.size,)
            elif t in _seqtypes:
                self.size = tuple(self.size)
            elif TypeCode.typechecks:
                raise TypeError('Size must be integer or list, not ' + str(t))

        if TypeCode.typechecks:
            if self.undeclared is False and type(atype) not in _seqtypes and len(atype) == 2:
                raise TypeError("Array type must be a sequence of len 2.")
            t = type(ofwhat)
            if not isinstance(ofwhat, TypeCode):
                raise TypeError(
                    'Array ofwhat outside the TypeCode hierarchy, ' +
                    str(ofwhat.__class__))
            if self.size:
                if len(self.size) != self.dimensions:
                    raise TypeError('Array dimension/size mismatch')
                for s in self.size:
                    if type(s) not in _inttypes:
                        raise TypeError('Array size "' + str(s) +
                                '" is not an integer.')
        self.ofwhat = ofwhat

    def parse_offset(self, elt, ps):
        o = _find_arrayoffset(elt)
        if not o: return 0
        if not _offset_pat.match(o):
            raise EvaluateException('Bad offset "' + o + '"',
                        ps.Backtrace(elt))
        return int(o[1:-1])

    def parse_position(self, elt, ps):
        o = _find_arrayposition(elt)
        if not o: return None
        if o.find(','):
            raise EvaluateException('Sorry, no multi-dimensional arrays',
                    ps.Backtrace(elt))
        if not _position_pat.match(o):
            raise EvaluateException('Bad array position "' + o + '"',
                    ps.Backtrace(elt))
        return int(o[-1:1])

    def parse(self, elt, ps):
        href = _find_href(elt)
        if href:
            if _children(elt):
                raise EvaluateException('Array has content and HREF',
                        ps.Backtrace(elt))
            elt = ps.FindLocalHREF(href, elt)
        if self.nilled(elt, ps): return Nilled
        if not _find_arraytype(elt) and self.undeclared is False:
            raise EvaluateException('Array expected', ps.Backtrace(elt))
        t = _find_type(elt)
        if t:
            pass # XXX should check the type, but parsing that is hairy.
        offset = self.parse_offset(elt, ps)
        v, vlen = [], 0
        if offset and not self.sparse:
            while vlen < offset:
                vlen += 1
                v.append(self.fill)
        for c in _child_elements(elt):
            item = self.ofwhat.parse(c, ps)
            position = self.parse_position(c, ps) or offset
            if self.sparse:
                v.append((position, item))
            else:
                while offset < position:
                    offset += 1
                    v.append(self.fill)
                v.append(item)
            offset += 1
        return v

    def serialize(self, elt, sw, pyobj, name=None, childnames=None, **kw):
        if self.mutable is False and sw.Known(pyobj): return
        objid = _get_idstr(pyobj)
        n = name or self.pname or ('E' + objid)
        el = elt.createAppendElement(self.nspname, n)

        # nillable
        if self.nillable is True and pyobj is None:
            self.serialize_as_nil(el)
            return None

        # other attributes
        self.set_attributes(el, pyobj)

        # soap href attribute
        unique = self.unique or kw.get('unique', False)
        if unique is False and sw.Known(orig or pyobj):
            self.set_attribute_href(el, objid)
            return None

        # xsi:type attribute 
        if kw.get('typed', self.typed) is True:
            self.set_attribute_xsi_type(el, **kw)

        # soap id attribute
        if self.unique is False:
            self.set_attribute_id(el, _get_idstr(pyobj))

        offset = 0
        if self.sparse is False and self.nooffset is False:
            offset, end = 0, len(pyobj)
            while offset < end and pyobj[offset] == self.fill:
                offset += 1
            if offset: 
                el.setAttributeNS(SOAP.ENC, 'offset', '[%d]' %offset)

        if self.undeclared is False:
            el.setAttributeNS(SOAP.ENC, 'arrayType', 
                '%s:%s' %(el.getPrefix(self.atype[0]), self.atype[1])
            )


        d = {}
        kn = childnames or self.childnames
        if kn:
            d['name'] = kn
        elif not self.ofwhat.aname:
            d['name'] = 'element'
        if self.sparse is False:
            for e in pyobj[offset:]: self.ofwhat.serialize(el, sw, e, **d)
        else:
            position = 0
            for pos, v in pyobj:
                if pos != position:
                    el.setAttributeNS(SOAP.ENC, 'position', '[%d]' %pos)
                    position = pos

                self.ofwhat.serialize(el, sw, v, **d)
                position += 1


if __name__ == '__main__': print _copyright
