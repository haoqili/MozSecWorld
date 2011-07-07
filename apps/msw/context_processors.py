from django.conf import settings

def global_settings(request):
    """
    Storing standard MSW-wide information used in global headers,
    such as settings.
    """

    context = {}

    context.update({'settings': settings})

    return context
