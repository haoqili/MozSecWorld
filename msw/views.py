# Create your views here.

from msw.models import Page
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, get_object_or_404

def index(request):
    # return HttpResponse("Hello, world. This is going to be where the Mozilla Secure World is going to be!")

    all_pages = Page.objects.all()
    rendered = render_to_response('mswTemplates/index.html', {"title_chunk" : "barbari", "all_pages_list": all_pages})
    return rendered


