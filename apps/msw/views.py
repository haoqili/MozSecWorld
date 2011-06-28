import jingo
import bleach
from msw.models import Page, RichText, RichTextForm
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, get_object_or_404
from django.db import connection, transaction
from django.utils import simplejson
# User Authentication / Login
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# urls.py's views. It renders the urls by putting in appropriate values into templates
# each def 
#       - corresponds to a template's html
#       - must return a HttpResponse. Simplest one is `return HttpResponse("Hello World!")`

# The dictionary maps keys for the template's {{ matching_key }} to its value. 
# The key/value can be for a list, because in the template, there is a for loop that goes through each value of the list.
#       e.g. index's Page.objects.all() is a list of all page (xss, sqlinjection)s

###########################
#### Login / Authentication

def login(request):
    if request.user.is_authenticated():
        print "\tUser already authenticated"
        return HttpResponse("already authenticated")

    if request.method == 'GET':
        return jingo.render(request, 'msw/registration/login.html', {"all_pages_list": Page.objects.all()}) #?? context_instance=RequestContext(request)??

    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    message = ""
    if user is not None:
        if user.is_active:
            # Redirect to a success page.
            login(request, user) # saves user ID in session
            message = "\tProvided correct un and pw"
        else:
            # Return a 'disabled account' error message
            message = "\tYour account has been disabled!"
    else:
        # Return an 'invalid login' error message.
        message = "\tYour username and password were incorrect."
    print message
    return HttpResponse(message)

# Decorators: https://docs.djangoproject.com/en/dev/topics/auth/#the-login-required-decorator
@login_required
def members_page(request):
    return HttpResponse("You're a member!")

def logout_page(request):
    # https://docs.djangoproject.com/en/dev/topics/auth/#storing-additional-information-about-users
    # When you call logout(), the session data for the current request is completely cleaned out. All existing data is removed.
    logout(request)
    return HttpResponse("You're logged out.")



########################
#### pages:

def index(request):
    rendered = jingo.render(request, 'msw/index.html', {"all_pages_list": Page.objects.all()})
    return rendered

def detail(request, input_slug):
    
    # get_object_or_404( model name, model attribute = value to test)
    # this function is analogous to Page.objects.filter(urlname=msw_urlname)
    # "urlname" is the attribute of the model, i.e. the column in the db table
    p = get_object_or_404(Page, slug=input_slug)


    return jingo.render(request, 'msw/detail.html', {"all_pages_list": Page.objects.all(), 'page':p})

def demo(request, input_slug):
    print input_slug

    p = get_object_or_404(Page, slug=input_slug)

    if input_slug == "set_cookie_httponly":
        response = jingo.render(request, 'msw/demos/'+input_slug+'.html', {"all_pages_list": Page.objects.all(), 'page':p})
        response.set_cookie('name1', 'Alice', httponly=False)
        response.set_cookie('name2', 'Bob', httponly=True)      # 'httponly=True' is optional since Playdoh automatically sets httponly to True


    if input_slug == "richtext_and_safe_url":
        test = bleach.clean('an <script>evil()</script> example')
        file = 'msw/demos/richtext_and_safe_url.html'
        if request.method == "POST":
            form = RichTextForm(request.POST)
            if form.is_valid():
                form.save()
            file = 'msw/demos/children/richtext_table.html'
        else:
            form = RichTextForm()
            
        #context_instance=RequestContext() is for the CSRF token
        response = jingo.render(request, file, {"all_pages_list": Page.objects.all(), "form": form, "title_chunk" : "Bleach Testing: "+test, "all_richtext_list": RichText.objects.all().order_by('-id'), 'page':p})
        return response


    response = jingo.render(request, 'msw/demos/'+input_slug+'.html', {"all_pages_list": Page.objects.all(), 'page':p})

    return response

def sql_ajax_server(request):
    if request.is_ajax():
        usrInput = request.POST
        myComment =  usrInput['comment']
        cursor = connection.cursor()

        # Data modifying operation - commit required
        print "myComment = " + str(myComment)
        cursor.execute("INSERT INTO msw_richtext SET name = 'sql_inj_test', comment = %s", [myComment])
        transaction.commit_unless_managed()


        # Data retrieval operation - no commit required
        # send back to client last 5 rows of richtext
        cursor.execute("SELECT name, comment from msw_richtext order by id desc limit 5", [])
        rows = cursor.fetchall()
        
        # convert to json!
        rows_json = simplejson.dumps(rows) 
        print rows_json
        return HttpResponse(rows_json)

    else:
        warning = "WARNING: SQL AJAX FAILED"        
        print warning
        return HttpResponse(warning)



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
def xfo_allow(request):
    html = "<html><body><p>This is a demonstration of a page that has 'X-Frame-Options: ALLOW', i.e. it does NOT HAVE 'X-Frame-Options: DENY'.</p><p>Open up the 'Net' in Firebug, refresh, clicke on 'GET ...', and 'X-Frame-Options: DENY' should not be seen in the HTTP 'Response Headers'.</p><p><h1><a href='/msw/x_frame_options/demo'>Back</a></h1></p></body></html>"
    response = HttpResponse(html)
    response['x-frame-options'] = 'ALLOW'
    return response
