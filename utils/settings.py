def debug_toolbar(apps: list, middleware: list, *, active: bool = True, **config):
    try:
        import debug_toolbar
    except ImportError:
        debug_toolbar = active = False

    ips = ['localhost', '127.0.0.1'] + ['192.168.0.%i' % ip for ip in range(1, 256)]

    if active:
        apps += [debug_toolbar.default_app_config]
        middleware = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + middleware
        config = dict(
            # Hide the debug toolbar by default.
            SHOW_COLLAPSED=True,

            # We disable the rarely used panels
            # by default to improve performance.
            DISABLE_PANELS={
                'debug_toolbar.panels.versions.VersionsPanel',
                'debug_toolbar.panels.timer.TimerPanel',
                'debug_toolbar.panels.settings.SettingsPanel',
                'debug_toolbar.panels.headers.HeadersPanel',
                'debug_toolbar.panels.request.RequestPanel',
                'debug_toolbar.panels.staticfiles.StaticFilesPanel',
                'debug_toolbar.panels.templates.TemplatesPanel',
                'debug_toolbar.panels.cache.CachePanel',
                'debug_toolbar.panels.signals.SignalsPanel',
                'debug_toolbar.panels.logging.LoggingPanel',
                'debug_toolbar.panels.redirects.RedirectsPanel',
            },
        )

    return active, ips, apps, middleware, config
