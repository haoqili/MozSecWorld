import jingo
import bleach
import urllib # to refresh recaptcha
from msw.models import Page, RichText, RichTextForm
from msw import forms

from commons.urlresolvers import reverse

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, get_object_or_404
from django.db import connection, transaction
from django.utils import simplejson
import json
# User Authentication / Login
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
# jsocol's ratelimiting https://github.com/jsocol/django-ratelimit
from ratelimit.decorators import ratelimit

#recaptcha refresh stuff:
import urllib
from django.conf import settings

# Access control stuff:
from django.contrib.auth.decorators import permission_required
from msw.models import MembersPostUser, MembersPostText, MembersPostSay


# urls.py's views. It renders the urls by putting in appropriate values into templates
# each def 
#       - corresponds to a template's html
#       - must return a HttpResponse. Simplest one is `return HttpResponse("Hello World!")`

# The dictionary maps keys for the template's {{ matching_key }} to its value. 
# The key/value can be for a list, because in the template, there is a for loop that goes through each value of the list.
#       e.g. index's Page.objects.all() is a list of all page (xss, sqlinjection)s

###########################
#### Login / Authentication

def recaptchaRefresh():
    # test from recaptcha_refreshTest.py
    # get the Recaptcha state.
    url = "https://www.google.com/recaptcha/api/challenge?k=%s" % settings.RECAPTCHA_PUBLIC_KEY
    resock = urllib.urlopen(url)
    data = resock.read()
    resock.close()

    # extract the recaptcha state part of the string
    docloc = data.find("document.write")

    recaptchaState = data[:docloc]

    f = open('media/js/google/recState.js', 'r+')
    f.write(recaptchaState)
    f.close()

# partially copied from default login view, vendor.src.django.django.cotrib.auth.views.py
@ratelimit(field='username', method='POST')
def login(request):
    was_limited = getattr(request, 'limited', False)
    #print "login was_limited = " + str(was_limited)
    redirect_to = reverse('membersOnly')

    hasRecaptcha = True
    if request.method == "POST":
        #: if exceeded threshould of 5 POSTS from save IP OR same username
        #:    then recaptcha is used
        if was_limited: 
            recaptchaRefresh()
            form = forms.AuthenticationCaptchaForm(request=request, data=request.POST)
        else:
            # this AuthenticationForm() takes care of a lot things, such as testing that the cookie worked
            hasRecaptcha = False
            form = forms.AuthenticationForm(request=request, data=request.POST)
        # is_valid() executes cleaning methods
        # https://docs.djangoproject.com/en/dev/ref/forms/validation/
        if form.is_valid(): 
            auth_login(request, form.get_user())

            # Check that the test cookie worked (we set it below):
            # for more info: http://www.djangobook.com/en/1.0/chapter12/
            if request.session.test_cookie_worked():
                # The test cookie worked, so delete it.
                request.session.delete_test_cookie()    
            
            return HttpResponseRedirect(redirect_to)
    else: 
        hasRecaptcha = False
        form = forms.AuthenticationForm(request=request)
    
    # If we didn't post, send the test cookie
    # along with the login form (set above).
    request.session.set_test_cookie()

    ctx = {
        'all_pages_list': Page.objects.all(),
        'form': form,
        'redirect_to': redirect_to,
        'has_recaptcha': hasRecaptcha,
    }

    return jingo.render(request, 'msw/demos/auth/login.html', ctx)


@ratelimit(field='username', method='POST')
def register(request):
    was_limited = getattr(request, 'limited', False)
    #print "register was_limited = " + str(was_limited)
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


@login_required
def membersOnly(request):
    message = "welcome to the super secret members-only page!"
    ctx = {
        'all_pages_list': Page.objects.all(),
        'message': message
    }
    return jingo.render(request, 'msw/demos/auth/membersOnly.html', ctx)
    
@permission_required('msw.superuser_display')
def membersPostSuper(request):
    print "YIPEEEEEE"
    message = "welcome to the ultra super secret ultra super members-only posting page!"
    ctx = {
        'all_pages_list': Page.objects.all(),
        'users_list': MembersPostUser.objects.all(),
        'all_texts_list': MembersPostText.objects.all(),        
        'message': message
    }
    return jingo.render(request, 'msw/demos/auth/membersPost.html', ctx)
    
def membersPost(request):
    if request.user.has_perm('msw.superuser_display'):
        print "YEAH!!!!!!!"
        return membersPostSuper(request)
    print "NOOOOOOO"
    message = "welcome to the super secret members-only posting page!"
    print "username:"
    print request.user.username
    print "users list:"
    print MembersPostUser.objects.all()
    print "------"
    oneUserList = set()
    #TODO: ask webdev how to do this better
    for person in MembersPostUser.objects.all():
        print person.user
        if person.user == request.user.username:
            oneUserList.add(person)
    ctx = {
        'all_pages_list': Page.objects.all(),
        'users_list': oneUserList,
        #'users_list': MembersPostUser.objects.get(username=request.user.username),
        #'users_list': MembersPostUser.objects.all(),
        'all_texts_list': MembersPostText.objects.all(),        
        'message': message
    }
    return jingo.render(request, 'msw/demos/auth/membersPost.html', ctx)

def ac_ajax_server(request):
    if request.is_ajax():
        print "at ac_ajax_server"
        tamperBoo = False

        usrInput = request.POST

        # Get the user from user id
        try: # Ensure the input is an integer
            inpUserId = int( usrInput['inpNameId'] )

            # check that the UserId is valid
            # step_0. get the user's id from server side
            serversUser = MembersPostUser.objects.get(user = request.user.username)
            serversUserId = int( serversUser.id )
            # step_1. If user is super, ID must be within the range of ids
            addUser = ""
            if request.user.has_perm('msw.superuser_display'):
                try: # Ensure the integer is valid
                    addUser = MembersPostUser.objects.get(id = inpUserId)
                except:
                    # TODO: Add CEF log say invalid integer range
                    tamperBoo = True
            # step_2. If user is not super, ID must match its userid
            else:
                if serversUserId == inpUserId:
                    addUser = MembersPostUser.objects.get(id = inpUserId)
                else:
                    tamperBoo = True
        except:
            # TODO: Add CEF log say invalid non-integer input
            tamperBoo = True

        # Get the Text, since the 2 tables are linked, must get text object!
        try: # Ensure the input is an integer
            inpTextId = int( usrInput['inpTextId'] )

            try: # Ensure the integer is valid
                addText = MembersPostText.objects.get(id = inpTextId)
            except:
                # TODO: Add CEF log say invalid integer range
                tamperBoo = True

            # put new entry into database
            if not tamperBoo:
                MembersPostSay.objects.create(mpuser=addUser, mptext=addText)
        except:
            # TODO: Add CEF log say invalid non-integer input
            tamperBoo = True
        
        # publish it
        file = 'msw/demos/children/ac_ajax_table.html'
        if tamperBoo:
            ctx = {
                "tamper_msg": "Please stop tampering"
            }
        else:
            ctx = {
                "all_postsay_list": MembersPostSay.objects.all().order_by('-id')
            }
        response = jingo.render(request, file, ctx)
        return response

        # Attempting JSON
        #print "&&&&&&&&&&&&&&&&&&&"
        #import pdb; pdb.set_trace()
        #jsontexts = json.dumps(texts)
        #print "*****************************" 
        #print jsontexts
        #return HttpResponse( jsontexts)

    else:
        # TODO: return a 404 or 405. (from cvan comment in 2343852088f41d521263819d12692bcabff3ebf6)
        warning = "WARNING: SQL AJAX FAILED"        
        print warning
        return HttpResponse(warning)


########################
#### pages:

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
        # TODO: return a 404 or 405. (from cvan comment in 2343852088f41d521263819d12692bcabff3ebf6)
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
