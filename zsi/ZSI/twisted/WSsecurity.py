###########################################################################
# Joshua R. Boverhof, LBNL
# See Copyright for copyright notice!
# $Id$
###########################################################################

import sys, warnings
import sha, base64

# twisted & related imports
from zope.interface import classProvides, implements, Interface
from twisted.python import log, failure
from twisted.web.error import NoResource
from twisted.web.server import NOT_DONE_YET
from twisted.internet import reactor
import twisted.web.http
import twisted.web.resource

# ZSI imports
from ZSI import _get_element_nsuri_name, EvaluateException, ParseException
from ZSI.parse import ParsedSoap
from ZSI.writer import SoapWriter
from ZSI.TC import _get_global_element_declaration as GED
from ZSI import fault
from ZSI.wstools.Namespaces import OASIS
from WSresource import DefaultHandlerChain, HandlerChainInterface,\
    WSAddressCallbackHandler, DataHandler, WSAddressHandler


# 
# Stability: Unstable, Untested, Not Finished.
# 

class WSSecurityHandler:
    """Web Services Security: SOAP Message Security 1.0
    """
    classProvides(HandlerChainInterface)
    targetNamespace = OASIS.WSSE

    @classmethod
    def processRequest(cls, ps, **kw):
        if type(ps) is not ParsedSoap:
            raise TypeError,'Expecting ParsedSoap instance'
        
        security = ps.ParseHeaderElements([GED(cls.targetNamespace,"Security")])
        
        # Assume all security headers are supposed to be processed here.
        for pyobj in security:
            for any in pyobj.Any or []:
                if any.typecode.pname == "UsernameToken":
                    cls.UsernameTokenProfileHandler.processRequest(any)
                    break
                
                raise RuntimeError, 'WS-Security, Unsupported token %s' %str(any)
            
        return ps

    @classmethod
    def processResponse(cls, output, **kw):
        return output


    class UsernameTokenProfileHandler:
        """Web Services Security UsernameToken Profile 1.0
        """
        classProvides(HandlerChainInterface)
        targetNamespace = OASIS.WSSE
        nonces = None
        PasswordDec = GED(targetNamespace, "Password")
        NonceDec = GED(targetNamespace, "Nonce")
        CreatedDec = GED(OASIS.UTILITY, "Created")
        addNonce = lambda cls,nonce,created:\
            UsernameTokenProfileHandler.nonces.append(nonce)
            
        # Set to None to disable
        PasswordText = targetNamespace + "#PasswordText"
        PasswordDigest = targetNamespace + "#PasswordDigest"
            
        # Override passwordCallback 
        passwordCallback = lambda cls,username: None
        
        @classmethod
        def sweep(cls, index):
            """remove expired nonces every 5 minutes.
            Parameters:
                index -- remove all nonces up to this index.
            """
            if cls.nonces is None: 
                cls.nonces = []
            
            seconds = 60*5
            cls.nonces = cls.nonces[index:]
            reactor.callLater(seconds, cls.sweep, len(cls.nonces))
        
        @classmethod
        def processRequest(cls, token, **kw):
            """
            token -- UsernameToken instance
            """
            username = token.Username
            
            # expecting only one password
            # may have a nonce and a created
            password = nonce = timestamp = None
            for any in token.Any or []:
                if any.typecode is cls.PasswordDec:
                    password = any
                    continue
                
                if any.typecode is cls.NonceTypeDec:
                    nonce = any
                    continue
                
                if any.typecode is cls.CreatedTypeDec:
                    timestamp = any
                    continue
                
                raise TypeError, 'UsernameTokenProfileHander unexpected %s' %str(any)

            if password is None:
                raise RuntimeError, 'Unauthorized, no password'
            
            # TODO: not yet supporting complexType simpleContent in pyclass_type
            attrs = getattr(password, password.typecode.attrs_aname, {})
            pwtype = attrs.get('Type', cls.PasswordText)
            
            # Clear Text Passwords
            if cls.PasswordText is not None and pwtype == cls.PasswordText:
                if password == cls.passwordCallback(username):
                    return
                
                raise RuntimeError, 'Unauthorized, clear text password failed'
            
            # PasswordDigest, recommended that implemenations
            # require a Nonce and Created
            if cls.PasswordDigest is not None and pwtype == cls.PasswordDigest:
                digest = sha.sha()
                for i in (nonce, created, cls.passwordCallback(username)):
                    if i is None: continue
                    digest.update(i)

                if password == base64.encodestring(digest.hexdigest()):
                    return
                
                raise RuntimeError, 'Unauthorized, digest failed'
            
            raise RuntimeError, 'Unauthorized, contents of UsernameToken unknown'
            
        @classmethod
        def processResponse(cls, output, **kw):
            return output
        

    class X509TokenProfileHandler:
        """Web Services Security UsernameToken Profile 1.0
        """
      
        @classmethod
        def processRequest(cls, ps, **kw):
            return ps

        @classmethod
        def processResponse(cls, output, **kw):
            return output



class WSSecurityHandlerChainFactory:
    protocol = DefaultHandlerChain
    
    @classmethod
    def newInstance(cls):
        if WSSecurityHandler.UsernameTokenProfileHandler.nonces is None:
            WSSecurityHandler.UsernameTokenProfileHandler.sweep(0)
            
        return cls.protocol(WSAddressCallbackHandler, DataHandler, 
            WSSecurityHandler, WSAddressHandler())



