# MozSecWorld
:D
Project [Website](https://wiki.mozilla.org/WebAppSec/MozSecureWorld).

# How I start
`workon playdoh` to go to Mozilla playdoh's environment

`mysql.server start` to start the MySQL database

`./manage.py runserver` starts the Django server so I can navigate to http://127.0.0.1:8000/msw/

# overview of files
    apps/msw/models.py --> mysql
    apps/msw/urls.py --> apps/msw/views.py --> apps/msw/templates/msw/*

# Addons
Add bleach: `pip install -e git://github.com/jsocol/bleach.git#egg=bleach` ... actually this has been updated to playdoh.
Download recaptcha-client http://pypi.python.org/pypi/recaptcha-client read http://curioushq.blogspot.com/2011/07/recaptcha-on-django.html

# For HTTPS URL certificate checking
- Use PyOpenSSL and sockets, not urllib, because urllib's urlopen does not check the SSL server certificates [warning on urllib documentation](http://docs.python.org/library/urllib.html), thus becoming vulnerable to Man-In-The-Middle attacks.
--> PyOpenSSL install: `pip install pyopenssl`

# Content security policy middleware:
- `git clone https://github.com/mozilla/django-csp.git` and then `cd django-csp` and `python setup.py install`

License
-------
TBD
