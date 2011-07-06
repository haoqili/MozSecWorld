import jinja2
from jingo import register

@register.function # kumar: register makes it available to jina templates
@jinja2.contextfunction
def media(context, url, key='MEDIA_URL'):
    """Get a MEDIA_URL link with a cache buster querystring."""
    if url.endswith('.js'):
        build = context['BUILD_ID_JS']
    elif url.endswith('.css'):
        build = context['BUILD_ID_CSS']
    else:
        build = context['BUILD_ID_IMG']
    return context[key] + utils.urlparams(url, b=build)
