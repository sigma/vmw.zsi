import sys

sys.path.insert (1, '..')

import SOAP

def usage():
    print sys.argv[0], "searchString"
    print '''\tcurrently, this can be used to search for word completions or
    anagrams- the function will parse and perform the word-search function if
    there is a "?" or "*" character, and perform the anagram-search function
    otherwise'''
    sys.exit(1)

if len(sys.argv) < 2: usage()

ss = sys.argv[1]

if ss.find('?') > -1 or ss.find('*') > -1: word=1
else: word=0
    
#SOAP.Config.debug = 1
serv = SOAP.SOAPProxy("http://webservices.matlus.com/scripts/WordFind.DLL/soap/IWordFind", namespace="urn:WordFindIntf-IWordFind", soapaction="urn:WordFindIntf-IWordFind#FindWords")
if word: print serv.FindWords(Source=ss)
else:
    serv._sa= ""
    print serv.FindAnagrams(Source=ss)
