import urllib
import bleach
import ssl
import socket           
import re
import datetime, time
from OpenSSL import SSL 
from django.conf import settings

####################################################
##### URL CHECK ####################################

# returns True if url is checked to be non-malicious, else False
# the 1 url's format must be "http://..."
def urlCheck(url):
    # following the google POST format
    # for more info: http://code.google.com/apis/safebrowsing/lookup_guide.html#HTTPPOSTRequestResponseBody
    urldata = "1\n" + url 

    if settings.GOOGLE_SAFEBROWSING_LOOKUP:
        # Google SafeBrowsing Lookup: http://code.google.com/apis/safebrowsing/lookup_guide.html#AQuickExamplePOSTMethod
        googleurl= settings.GSB_HOST + settings.GSB_PATH + "?client=api&apikey=" + settings.GSB_API_KEY + "&appver=1.5.2&pver=3.0"

        # check that there is not a MITM of the host by validating the certificates
        google_hosturl = getUrl(settings.GSB_HOST) # takes out "http://"
        certValid = validateCert(google_hosturl)

        # there is a MITM, don't bother connecting to the google url
        if not certValid[0]:
            return False

        # Safe to visit the google lookup url
        f = urllib.urlopen(googleurl, urldata)
        response_code = f.code

        # the url is safe 
        if response_code == 204:
            return True 
    return False

# ValidateHTTPS Server certificate from http://wiki.python.org/moin/SSL
def validateCert(url):
    #print url # should match sb-ssl.google.com
    certValid = [False]

    print "\n\n"
    print "==========================================================================="
    print "========= Validating Certificate for " + str(url) + " ========"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #The ca_certs file must be valid or all cert checks will fail
    certFile = "apps/msw/files/ca-bundle.crt" # same idea as cacerts.txt, maybe same
    ssl_sock = ssl.wrap_socket(s,
                               ca_certs=certFile,
                               cert_reqs=ssl.CERT_REQUIRED,
                               ssl_version=ssl.PROTOCOL_SSLv3)   # hq added for certerror        
    ssl_sock.connect((url, 443))
    peerCert=ssl_sock.getpeercert()
    #print "PERR CERT:"
    #print peerCert 
    print "\n------- Step 1: Validating certificate matches url hostname ----"
    try : 
        # STEP 1. VERIFY THAT THERE IS A CERTIFICATE
        # match_hostname url: https://bitbucket.org/brandon/backports.ssl_match_hostname/src/67f1340d302d/__init__.py
        match_hostname(peerCert, url)
        print "\r\n Certificate Check Step 1 Passed -- There is a certificate for URL"
    except CertificateError, ce: 
        print "\r\n Certificate Check Step 1 FAILED -- No certificate for URL"
        print "Certificate Error at Step 1: Validating that certificate matches url hostname: " + str(url)
        print ce
        print "\r\n Skipping rest of certification check"
        return certValid # certValid[0] already set to False

    print "\n------- Step 2: Verify that the certificate is not expired  --------------"
    for k, v in peerCert.iteritems():
        # STEP 2. VERIFY CERTIFICATE IS NOT EXPIRED Certificate Expiration Checking
        if k=='notAfter':
            todayDate= datetime.date.today()
            #http://docs.python.org/library/time.html
            format='%b %d %H:%M:%S %Y %Z'
            tempExpDate= time.strptime(v, format)
            #print time.mktime(tempExpDate)
            year = tempExpDate.__getattribute__('tm_year')
            month = tempExpDate.__getattribute__('tm_mon')
            day = tempExpDate.__getattribute__('tm_mday')
            expDate=datetime.date(year, month, day)

            tillExpiration= expDate-todayDate
            if tillExpiration < datetime.timedelta (days = 30):
                print "\r\n Certificate Check Step 2 FAILED -- Certificate HAS EXPIRED, expiring in %s" % tillExpiration
                print "\r\n Skipping rest of certification check"
                return certValid # certValid[0] already set to False
            else:
                print "\r\n Certificate Check Step 2 Passed -- Certificate not expired, expiring in %s" % tillExpiration

    print "\n------- Step 3: Validating the chain of CAs  --------------"
    # crucially MODIFIED from: http://wiki.python.org/moin/SSL
    #url = "sb-ssl.google.com" # what the url should be
    #url = "www.google.com" # for testing
    PORT = 443

    host = url
    print "For host = " + str(host)

    # uses host
    def verify_cb(conn, x509, errno, errdepth, retcode):
        """
        callback for certificate validation
        should return true if verification passes and false otherwise
        """
        print "   CA = " + str( x509.get_subject() )
 
        if errno == 0:
            if errdepth != 0:
                # don't validate names of root certificates
                print "\t---> GOOD (root certificate)"
                certValid[0] = True
                return True
            else:
                certComName = x509.get_subject().commonName
                # the certComName might be like "*.google.com" ==> regex: .*\.google\.com
                # Have to check that * does not contain any "." => regex: (.*)\.google\.com
                #     e.g. (.*) can be "x" but not "x.y" (that way host name is different)
                # change    "." --> "\."   "*" --> "(.*)" order matters
                starNum = certComName.count("*") # number of asterisks
                certComName = certComName.replace(".", "\.")
                certComName = certComName.replace("*", "(.*)")
                result = re.match(certComName, host) # certComName == host with * interpretation
                if result:
                    # If (.*) matches any dots, return False!
                    # reference: http://docs.python.org/library/re.html#re.MatchObject.group
                    for i in range(1, starNum+1):
                        if "." in result.group(i):
                            print "\t---> FAILED (cert commonName does not meet requirment)"
                    # if got out of that for loop, that means * regions don't have any dots :D
                    print "\t---> GOOD (cert commonName matched host name)"
                    certValid[0] = True
                    return True
                else:
                    print "\tcertCommonName: \t" + str(certComName)
                    print "\thostName: \t\t" + str(host)
                    print "\t---> FAILED (cert commonName did not match host name)"
                    certValid[0] = False
                    return False
        else:
            print "\t---> FAILED"
            certValid[0] = False
            return False

    context = SSL.Context(SSL.SSLv23_METHOD)
    context.set_verify(SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT, verify_cb)
    context.load_verify_locations("apps/msw/files/cacerts.txt")

    # create socket and connect to server
    sock = socket.socket()
    sock = SSL.Connection(context, sock)
    sock.connect((host, PORT))
    try:
        sock.do_handshake()
    except Exception as ec:
        print ec

    if certValid[0]:
        print "\r\n Certificate Check Step 3 Passed -- Chain of CAs is valid"
        print "\r\n HOST IS GOOD! :)"
    else:
        print "\r\n Certificate Check Step 3 FAILD -- Chain of CAs is NOT VALID"
        print "\r\n HOST IS BAD! :("

    print "\n=============== End Validating the Certificate of URL = " + str(url)
    print "==========================================================================="
    return certValid

# strips "http://" or "https://" 
def getUrl(str):
    if "http://" in str:
        return str.replace("http://", "")
    if "https://" in str:
        return str.replace("https://", "")
    return str

##### URL CHECK ####################################
####################################################


##########################################################################
##########################################################################
############# ssl_match_hostname #########################################

"""The match_hostname() function from Python 3.2, essential when using SSL."""

#import re

__version__ = '3.2a3'

class CertificateError(ValueError):
    pass

def _dnsname_to_pat(dn):
    pats = []
    for frag in dn.split(r'.'):
        if frag == '*':
            # When '*' is a fragment by itself, it matches a non-empty dotless
            # fragment.
            pats.append('[^.]+')
        else:
            # Otherwise, '*' matches any dotless fragment.
            frag = re.escape(frag)
            pats.append(frag.replace(r'\*', '[^.]*'))
    return re.compile(r'\A' + r'\.'.join(pats) + r'\Z', re.IGNORECASE)

def match_hostname(cert, hostname):
    """Verify that *cert* (in decoded format as returned by
    SSLSocket.getpeercert()) matches the *hostname*.  RFC 2818 rules
    are mostly followed, but IP addresses are not accepted for *hostname*.

    CertificateError is raised on failure. On success, the function
    returns nothing.
    """
    if not cert:
        raise ValueError("empty or no certificate")
    dnsnames = []
    san = cert.get('subjectAltName', ())
    for key, value in san:
        if key == 'DNS':
            if _dnsname_to_pat(value).match(hostname):
                return
            dnsnames.append(value)
    if not san:
        # The subject is only checked when subjectAltName is empty
        for sub in cert.get('subject', ()):
            for key, value in sub:
                # XXX according to RFC 2818, the most specific Common Name
                # must be used.
                if key == 'commonName':
                    if _dnsname_to_pat(value).match(hostname):
                        return
                    dnsnames.append(value)
    if len(dnsnames) > 1:
        raise CertificateError("hostname %r "
            "doesn't match either of %s"
            % (hostname, ', '.join(map(repr, dnsnames))))
    elif len(dnsnames) == 1:
        raise CertificateError("hostname %r "
            "doesn't match %r"
            % (hostname, dnsnames[0]))
    else:
        raise CertificateError("no appropriate commonName or "
            "subjectAltName fields were found")
