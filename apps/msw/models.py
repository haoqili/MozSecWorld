import urllib
import bleach
import socket           # validate server certificate
from OpenSSL import SSL # validate server certificate
from django.db import models
from django.forms import ModelForm
from django.template.defaultfilters import slugify
from django.conf import settings


# Django automatically creates a table for each "class" here, named "[app name]_[class name]"
# so the table of "class Page" is "msw_page"
# each attribute of a class corresponds to a column in its table
class Page(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=100)
    summary = models.CharField(max_length=1000)
    description = models.TextField()
    prevention = models.TextField()
    demo = models.CharField(max_length=2000)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.slug)
        super(Page, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

class RichText(models.Model):
    name = models.CharField(max_length=200)
    comment = models.TextField()

    def __unicode__(self):
        return self.name + ": " + self.comment


# returns True if url is checked to be non-malicious, else False
# the 1 url's format must be "http://..."
def urlCheck(url):
    data = "1\n" + url
    if settings.GOOGLE_SAFEBROWSING_LOOKUP:
        # Google SafeBrowsing Lookup: http://code.google.com/apis/safebrowsing/lookup_guide.html#AQuickExamplePOSTMethod
        f = urllib.urlopen(settings.GSB_URL + "?client=api&apikey=" + settings.GSB_API_KEY + "&appver=1.5.2&pver=3.0", data)
        response_code = f.code
        # print f.read() # prints out the response (for multiple URLS)
        # for more info: http://code.google.com/apis/safebrowsing/lookup_guide.html#HTTPPOSTRequestResponseBody
        if response_code == 204:
            return True 
    return False

# ValidateHTTPS Server certificate from http://wiki.python.org/moin/SSL
def validateCert(url):
    print
    print "------- Validating the Certificate of URL = " + str(url)
    #url = "www.google.com"
    PORT = 443

    certValid = [False]

    # replace host name with IP, this should fail connection attempt,
    # but it doesn't by default
    host = socket.getaddrinfo(url, PORT)[0][4][0]

    # uses host
    def verify_cb(conn, x509, errno, errdepth, retcode):
        """
        callback for certificate validation
        should return true if verification passes and false otherwise
        """
        print "CA = " + str( x509.get_subject() )
 
        if errno == 0:
            if errdepth != 0:
                # don't validate names of root certificates
                certValid[0] = True
                print "\t---> PASSED (just 1 pass is enough for now)"
                return True
            else:
                if x509.get_subject().commonName != host:
                    print "\t---> failed"
                    return False
        else:
            print "\t---> failed"
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
    print "------- End Validating the Certificate of URL = " + str(url) + "\n"
    return certValid

# strips "http://" or "https://" 
def getUrl(str):
    if "http://" in str:
        return str.replace("http://", "")
    if "https://" in str:
        return str.replace("https://", "")
    return str

# ModelForm https://docs.djangoproject.com/en/dev/topics/forms/modelforms/
class RichTextForm(ModelForm):
    class Meta:
        model = RichText
    
    def clean_name(self):
        data = self.cleaned_data['name']
        #is it an URL?...does it have "http"
        # ASSUMING the ENTIRE NAME FIELD is a URL that starts with http:// or https://
        # ASSUMING THAT THE URL IS VALID!!!!!!!! (or else validateCert hangs)
        if "http" in data:
            if urlCheck(data):
                data = data # not adding any modifications to daat

                # if check certificates
                url = getUrl(data) # takes out "http://"
                certValid = validateCert(url)

                # adds href to data
                data = bleach.linkify(data)
    
                # print the output of check certificates
                if certValid[0]:
                    data = data + " <-- url has valid certificate"
                else:
                    data = data + " <-- url does not have valide certificate"
            else:
                data = data+"DANGEROUS LINK!!!!!!!"
        return bleach.clean(data)

    def clean_comment(self): #comment must match one of the fields of model
        data = self.cleaned_data['comment']
        return bleach.clean(data)
