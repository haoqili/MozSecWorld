import jingo
import bleach
from msw.models import Page, RichText, RichTextForm
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, get_object_or_404

# urls.py's views. It renders the urls by putting in appropriate values into templates
# each def 
#       - corresponds to a template's html
#       - must return a HttpResponse. Simplest one is `return HttpResponse("Hello World!")`

# The dictionary maps keys for the template's {{ matching_key }} to its value. 
# The key/value can be for a list, because in the template, there is a for loop that goes through each value of the list.
#       e.g. index's Page.objects.all() is a list of all page (xss, sqlinjection)s

def index(request):
    rendered = jingo.render(request, 'msw/index.html', {"all_pages_list": Page.objects.all()})
    return rendered

def detail(request, input_slug):
    
    # get_object_or_404( model name, model attribute = value to test)
    # this function is analogous to Page.objects.filter(urlname=msw_urlname)
    # "urlname" is the attribute of the model, i.e. the column in the db table
    p = get_object_or_404(Page, slug=input_slug)


    return jingo.render(request, 'msw/detail.html', {'page':p})

def demo(request, input_slug):
    print input_slug

    p = get_object_or_404(Page, slug=input_slug)

    rendered = jingo.render(request, 'msw/demos/'+input_slug+'.html', {'page':p})
    return rendered
    

def cookie(request):
    rendered = jingo.render(request, 'msw/cookie.html', {"title_chunk" : "Cookie Testing", "all_pages_list": Page.objects.all()})
    return rendered

# X-Frame-Options
def xfo_deny(request):
    html = "<html><body><p>This is a demonstration of a page that has 'X-Frame-Options: DENY'.</p><p>Open up the 'Net' in Firebug, refresh, clicke on 'GET ...', and 'X-Frame-Options: DENY' should be in the HTTP 'Response Headers'.</p><p><h1><a href='/msw/x_frame_options/demo'>Back</a></h1></p></body></html>"
    response = HttpResponse(html)
    response['x-frame-options'] = 'DENY'
    return response

# X-Frame-Options
def xfo_sameorigin(request):
    html = "<html><body><p>This is a demonstration of a page that has 'X-Frame-Options: SAMEORIGIN'.</p><p>Open up the 'Net' in Firebug, refresh, clicke on 'GET ...', and 'X-Frame-Options: SAMEORIGIN' should be in the HTTP 'Response Headers'.</p><p><h1><a href='/msw/x_frame_options/demo'>Back</a></h1></p></body></html>"
    response = HttpResponse(html)
    response['x-frame-options'] = 'SAMEORIGIN'
    return response

# X-Frame-Options
def xfo_false(request):
    html = "<html><body><p>This is a demonstration of a page that has 'X-Frame-Options: FALSE', i.e. it does NOT HAVE 'X-Frame-Options: DENY'.</p><p>Open up the 'Net' in Firebug, refresh, clicke on 'GET ...', and 'X-Frame-Options: DENY' should not be seen in the HTTP 'Response Headers'.</p><p><h1><a href='/msw/x_frame_options/demo'>Back</a></h1></p></body></html>"
    response = HttpResponse(html)
    response['x-frame-options'] = 'FALSE'
    return response



# HTTP Only Demo : Positive
def set_httponly(request):
    html = "<html><body><p>This is a demonstration of a page that has 'Set-Cookie: HTTPOnly'.</p><p>Open up the 'Net' in Firebug, refresh, clicke on 'GET ...', and 'httponly;' should be in the HTTP 'Response Headers'.</p><p><h1><a href='/msw/set_cookie_httponly/demo'>Back</a></h1></p></body></html>"
    response = HttpResponse(html)
    #response = HttpResponse('')
    response.set_cookie('foo', 'bar')
    return response

# HTTP Only Demo : Negative
def no_httponly(request):
    html = "<html><body><p>This is a demonstration of a page that does not have 'Set-Cookie: HTTPOnly'.</p><p>Open up the 'Net' in Firebug, refresh, clicke on 'GET ...', and 'httponly;' should not be seen in the HTTP 'Response Headers'.</p><p><h1><a href='/msw/set_cookie_httponly/demo'>Back</a></h1></p></body></html>"
    response = HttpResponse(html)
    #response = HttpResponse('')
    response.set_cookie('foo', 'bar', httponly=False)
    return response

def richtext(request):
    #import pdb; pdb.set_trace() # debugging in the server outoputs
    '''> /Users/haoqili/dev/playdoh/playdoh/playdoh/apps/msw/views.py(42)richtext()
    -> test = bleach.clean('an <script>evil()</script> example')
    (Pdb) request.method
    'GET
    '''
    test = bleach.clean('an <script>evil()</script> example')
    file = 'msw/richtext.html'
    if request.method == "POST":
        form = RichTextForm(request.POST)
        if form.is_valid():
            form.save()
        file = 'msw/richtext_table.html'
    else:
        form = RichTextForm()
        
    #context_instance=RequestContext() is for the CSRF token
    rendered = jingo.render(request, file, {"form": form, "title_chunk" : "Bleach Testing: "+test, "all_richtext_list": RichText.objects.all().order_by('-id')})
    return rendered 
