# Create your views here.

from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. This is going to be where the Mozilla Secure World is going to be!")


