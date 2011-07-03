import pprint
import jingo
import bleach
from msw.models import Page, RichText, RichTextForm
from msw import forms

from commons.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, get_object_or_404
from django.db import connection, transaction
from django.utils import simplejson
# User Authentication / Login
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
# jsocol's ratelimiting https://github.com/jsocol/django-ratelimit
from ratelimit.decorators import ratelimit

# urls.py's views. It renders the urls by putting in appropriate values into templates
# each def 
#       - corresponds to a template's html
#       - must return a HttpResponse. Simplest one is `return HttpResponse("Hello World!")`

# The dictionary maps keys for the template's {{ matching_key }} to its value. 
# The key/value can be for a list, because in the template, there is a for loop that goes through each value of the list.
#       e.g. index's Page.objects.all() is a list of all page (xss, sqlinjection)s

###########################
#### Login / Authentication

# partially copied from default login view, vendor.src.django.django.cotrib.auth.views.py
def login(request):
    redirect_to = reverse('mswindex')
    if request.user.is_authenticated():
        print "Welcome. You're already logged in. Username: "
        print request.user
    else:
        print "New user, please log in. Username?:"
        print request.user

    if request.method == "POST":
        print "Inside POST"
        # aeou
        form = forms.AuthenticationForm(request=request, data=request.POST, only_active=True)
        if form.is_valid():
            print "\n@ IS VALID"
            print "isvaild ------------------------"
            print request.session
            print "isvalid - - - - - - -- - - - -"
            print "isvaild keys:"
            print request.session.keys()
            print "isvalid items:"
            print request.session.items()
            print "isvalid &&&&&&&&&&&&&&&&&&&&&&&&"
            auth_login(request, form.get_user())

            # Check that the test cookie worked (we set it below):
            # for more info: http://www.djangobook.com/en/1.0/chapter12/
            if request.session.test_cookie_worked():
                print "\n@ TEST COOKIE WORKED!!!"
                print "cookWorked ------------------------"
                print request.session
                print "cookWorked - - - - - - -- - - - -"
                print "cookWorked keys:"
                print request.session.keys()
                print "cookWorked items:"
                print request.session.items()
                print "cookWorked &&&&&&&&&&&&&&&&&&&&&&&&"
                # The test cookie worked, so delete it.
                request.session.delete_test_cookie()    
                print "cookWorked after DELETED keys:"
                print request.session.keys()
                print "cookWorked after DELETED items:"
                print request.session.items()
                # the "else" case ... when test cookie failed case is at "def check_for_test_cookie()" in contrib/auth/forms.py?
            else: # put it here just in case
                print "Cookies NOT ENABLED! Should enable cookies and try again."
                #return HttpResponse("Please enable cookies and try again.")
            
            return HttpResponseRedirect(redirect_to)
    else: 
        form = forms.AuthenticationForm(request=request)
    
    # If we didn't post, send the test cookie
    # along with the login form (set above).
    request.session.set_test_cookie()
    print "\n@ SET COOKIE"
    print "setcook ------------------------"
    print request.session
    print "setcook - - - - - - -- - - - -"
    print "setcook keys:"
    print request.session.keys()
    print "setcook items:"
    print request.session.items()
    print "setcook &&&&&&&&&&&&&&&&&&&&&&&&"

    ctx = {
        'all_pages_list': Page.objects.all(),
        'form': form,
        'redirect_to': redirect_to
    }

    return jingo.render(request, 'msw/demos/auth/login.html', ctx)


@ratelimit(field='username', method='POST')
def register(request):
    was_limited = getattr(request, 'limited', False)
    print "WASSSSSSSSSS:"
    print was_limited
    message = ""
    if request.user.is_authenticated():
        message = "You are already logged in to an account."
        form = None
    elif request.method == 'POST':

        # "Handling Registration" http://www.djangobook.com/en/1.0/chapter12/        
        if was_limited: # exceeded threshold
            form = forms.UserCreationCaptchaForm(data=request.POST)
        else:
            form = forms.UserCreationForm(data=request.POST)

        if form.is_valid():
            form.save()
            #person = form.cleaned_data["username"]
            print "VALID REGISTER FORM :D:D:D:D:D:D:D:D!"
            message = "registered"

            # TODO: run authenticate on the user, so we automatically log them in.
            # redirect to login page
            return HttpResponseRedirect(reverse('login'))
        else:
            message = "invalid information"
    else:
        print "New registration form"
        if was_limited: # exceeded threshold
            form = forms.UserCreationCaptchaForm()
        else:
            form = forms.UserCreationForm()
            
    ctx = {
        'all_pages_list': Page.objects.all(),
        'form': form,
        'message': message
    }
    return jingo.render(request, 'msw/demos/auth/register.html', ctx)


def logout(request):
    # https://docs.djangoproject.com/en/dev/topics/auth/#storing-additional-information-about-users
    # When you call logout(), the session data for the current request is completely cleaned out. All existing data is removed.
    if request.user.is_authenticated():
        print "Logging out authenticated user"
        auth_logout(request)
        message = "logged out!! :D"
    else:
        message =  "not logged in, so no need to log out"
        print message
    ctx = {
        'all_pages_list': Page.objects.all(),
        'message': message
    }
    return jingo.render(request, 'msw/demos/auth/logout.html', ctx)



########################
#### pages:

@login_required
def index(request):
    print "^ ^ ^ ^ ^ Welcome to the Index Page ^ ^ ^ "
    print "request.user: "
    print request.user
    if request.user.is_authenticated():
        print "@ IndexPage and You're logged in :DDDDDDD"
    else:
        print "@ IndexPage and You're NOT LOGGED IN :( :(:(:("
        print "\n@ Index page"
        print "indexPage ------------------------"
        print request.session
        print "indexPage - - - - - - -- - - - -"
        print "indexPage keys:"
        print request.session.keys()
        print "indexPafe items:"
        print request.session.items()
        print "&&&&&&&&&&&&&&&&&&&&&&&&"
        print "@ IndexPage and Not logged in :(:(:(:(:("
    if request.method == "GET":
        rendered = jingo.render(request, 'msw/index.html', {"all_pages_list": Page.objects.all()})
        if 'next' in request.GET:
            print "XXXXXXXXXXXXXXXXXXXXXXXXXXX" 
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
    html = """<html><body><p>This is a demonstration of a page that has 'X-Frame-Options: ALLOW', i.e. it does NOT HAVE 'X-Frame-Options: DENY'.</p><p>Open up the 'Net' in Firebug, refresh, clicke on 'GET ...', and 'X-Frame-Options: DENY' should not be seen in the HTTP 'Response Headers'.</p><p><h1><a href='/msw/x_frame_options/demo'>Back</a></h1></p></body></html>"""
    response = HttpResponse(html)
    response['x-frame-options'] = 'ALLOW'
    return response
