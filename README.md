# MozSecWorld

Project [Website](https://wiki.mozilla.org/WebAppSec/MozSecureWorld).

# How I start
`workon playdoh` to go to Mozilla playdoh's environment

`mysql.server start` to start the MySQL database

`./manage.py runserver` starts the Django server so I can navigate to http://127.0.0.1:8000/msw/

# overview of files
    apps/msw/models.py --> mysql
    apps/msw/urls.py --> apps/msw/views.py --> apps/msw/templates/msw/*

License
-------
TBD
