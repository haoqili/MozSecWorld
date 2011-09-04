Things to try to help with the slowness speed issue


Locale
==============

description
------------

- i18n 
    - LocaleURLMiddleware
    - urlresolvers.reverse --> use default django reverse (mgoodwin's pull request)
- L10n

person responsible
------------------

- HaoQi, with help from Mark and Michael

progress
----------

- HaoQi is still getting 404's
- Mark has gotten rid of i18n from the changes made in his pull request

webifyme config
===============

description
------------

14:18 <ErikRose> The webifyme folks say "when webifyme was running really slow on dev, it was because this was not defined: WSGIDaemonProcess webifyme processes=4 threads=1 
                 maximum-requests=200 display-name=webifyme WSGIProcessGroup webifyme"
14:19 <mcoates> so that extra config was added?
14:19 <ErikRose> Apparently, yes.

person responsible
------------------

- shyam

progress
----------

- ??

X Get rid of db Page requests
===========================

description
------------

not request all the objects every time (Page.objects.all()). Is "all_pages_list" being used at all? Can that be removed?
https://github.com/haoqili/MozSecWorld/blob/master/apps/msw/views.py#L355
(Erik)

person responsible
------------------

- HaoQi

progress
----------

- done

X Template render once only
=========================

description
------------

The template is rendered twice for no reason. Line 355 and 358.

person responsible
------------------

- HaoQi

progress
----------

- done

Print statements
===================

description
------------

We can also get rid of the print statements that are just in there for debugging. This may also be slowing things down.


person responsible
------------------

- HaoQi

progress
----------

- fixed most
