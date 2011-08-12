About MozSecWorld
=========
MozSecWorld is a reference site to help web developers make their sites more secure. It is a running Django web application demonstrating major security paradigms used within Mozilla web applications and security capabilities of modern browsers. Each security feature comes with a live demo, complete with explanations, diagrams, and code.

Like other Mozilla projects, MozSecWorld is [completely open source][14]. Feel free to comment, critique, or contribute. 

MozSecWorld is running at [https://mozsecworld.org][30], the site will be fully functional by September 20th, 2011..

List of Demos
===========

Cross Domain

* x-frame-options: DENY
* set-cookie: HTTPOnly
* Content Security Policy

Input Validation

* Parameterized SQL statements
* Richtext, so users can use &lt;i&gt;, &lt;b&gt;, but not &lt;script&gt;
   * [bleach][11] only allows whitelisted HTML tags
* Only safe URLs are clickable
   * Google SafeBrowsing and a 3-step HTTPS Google Validation
* Image Upload following the [“Image Upload” guidelines][13]
   * strip away extraneous content with PIL rewrite

Good Authentication

* Password safety with bcrypt+HMAC
* Black-listed passwords
* Brute force prevention with [ratelimit][12] and ReCapatcha
   * Shows ReCaptach after multiple failed logins from same IP or different IP for same username

Access Control

* Access Control: separate Presentation, Business, and Data layers

Transport Security [coming soon]

* Full and correct TLS
* HTTP Strict Transport Security

Setup
========

1. Get the repository: `git clone https://github.com/haoqili/MozSecWorld`

2. Get the vendor: `cd MozSecWorld/vendor` and do `git clone --recursive git://github.com/mozilla/playdoh-lib.git .`
 * update jingo-minify because an older version might be referenced in the submodule: `cd vendor/src/jingo-minfy && git fetch origin && git checkout origin/master`

3. Configure settings: `cp settings_local.py-dist settings_local.py`
 * and then put in an account's user and password in `settings_local.py`, for example `'USER' : 'msw_user', 'PASSWORD' : 'm3dRL2Asw7'`
 * [Get Google Safe Browsing Key][5] and fill it in on settings_local.py
 * [Get Recaptcha keys][6] and fill it in on settings_local.py

* Mysql setup: 
 * get mysql server: `sudo apt-get install mysql-server`
 * `mysql -u root -p`
 * mysql> `show databases;`
 * mysql> `select user, host from myqsl.user;`
 * mysql> `grant all on mozsecworld.* to msw_user@localhost identified by 'm3dRL2Asw7';`
 * mysql> `create database mozsecworld;`

5. Get pip: `sudo apt-get install python-pip`

6. Get bcrypt: `sudo pip install py-bcrypt`. If you have rhel, you can do `yum install py-bcrypt`

7. Get jinja2: `sudo pip install jinja2`

9. run the server: `python manage.py runserver` and you should see

    Validating models...
    0 errors found
    ...

10. go to 127.0.0.1:8000/msw and you should see a green-themed page :D

TODO: add default mysql

TODO: try `pip install -r requirements/compiled.txt`

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

CEF: inside your project home dir, do: `pip install --no-install --build=vendor-local/packages --src=vendor-local/src -I cef` [for more info][1]

[Image Upload][2]
* PIL: inside your project home dir, do: `pip install --no-install --build=vendor-local/packages --src=vendor-local/src -I pil`
* Jpeg: `brew install jpeg`
* rebuild PIL: `pip install PIL==1.1.7 --upgrade`

# For HTTPS URL certificate checking
- Use PyOpenSSL and sockets, not urllib, because urllib's urlopen does not check the SSL server certificates [warning on urllib documentation](http://docs.python.org/library/urllib.html), thus becoming vulnerable to Man-In-The-Middle attacks.
--> PyOpenSSL install: `pip install pyopenssl`


[1]: http://curioushq.blogspot.com/2011/07/django-playdoh-package-locations.html
[2]: http://curioushq.blogspot.com/2011/07/getting-image-upload-to-work-on-django.html
[3]: http://pypi.python.org/pypi/setuptools#files
[4]: http://pypi.python.org/pypi/setuptools
[5]: http://code.google.com/apis/safebrowsing/key_signup.html
[6]: http://www.google.com/recaptcha/whyrecaptcha

[11]: https://github.com/jsocol/bleach
[12]: https://github.com/jsocol/django-ratelimit
[13]: https://wiki.mozilla.org/WebAppSec/Secure_Coding_Guidelines#Uploads
[14]: https://github.com/haoqili/MozSecWorld 

[30]: https://mozsecworld.org/en-US/msw/
