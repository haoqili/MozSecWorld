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
    rendered = jingo.render(request, 'msw/index.html', {"title_chunk" : "aaiiibarbari", "all_pages_list": Page.objects.all()})
    return rendered

def detail(request, input_slug):
    
    # get_object_or_404( model name, model attribute = value to test)
    # this function is analogous to Page.objects.filter(urlname=msw_urlname)
    # "urlname" is the attribute of the model, i.e. the column in the db table
    p = get_object_or_404(Page, slug=input_slug)


    return jingo.render(request, 'msw/detail.html', {'page':p})

def cookie(request):
    rendered = jingo.render(request, 'msw/cookie.html', {"title_chunk" : "Cookie Testing", "all_pages_list": Page.objects.all()})
    return rendered

def set_cookie(request):
    response = HttpResponse('')
    response.set_cookie('foo', 'bar')
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
