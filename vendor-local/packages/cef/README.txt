==========
CEF logger
==========


Most Mozilla Services applications need to generate CEF logs. A CEF Log is a
formatted log that can be used by ArcSight, a central application used
by the infrasec team to manage application security.

The *cef* module provide a `log_cef` function that can be used to
emit CEF logs:

    log_cef(message, severity, environ, config, [username,
            [signature]], \*\*kw)

    Creates a CEF record, and emit it in syslog or another file.

    Args:
        - message: message to log
        - severity: integer from 0 to 10
        - environ: the WSGI environ object
        - config: configuration dict
        - signature: CEF signature code, defaults to 'AuthFail'
        - username: user name, defaults to 'none'
        - extra keywords: extra keys used in the CEF extension

Example::

    >>> from cef import log_cef
    >>> log_cef('SecurityAlert!', 5, environ, config,
    ...         msg='Someone has stolen my chocolate')


With *environ* and *config* provided by the web environment.

You can use the cef module with pythons logging module.

Example of logging configuration::

        'syslog': {
            '()': cef.SysLogFormatter,
            'datefmt': '%H:%M:%s',
        },

Send message to the log::

        log_file.warning('Something', {environ: environ,
                                       username: request.user,
                                       data: data})

The SysLogFormatter will use the date format set in the log configuration
(datefmt). It will convert the logging error level into a sys log error level.

CEF specific fields (version, vendor, device_version, product) can be also
be provided, defaults will be used if not passed.
