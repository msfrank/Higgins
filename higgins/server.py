# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import sys, pwd, grp, os
from django.core.management import call_command as django_admin_command
from twisted.python import usage
from twisted.python.logfile import LogFile
from higgins.site_settings import site_settings
from higgins import logger, VERSION

class ServerException(Exception):
    def __init__(self, reason):
        self.reason = reason
    def __str__(self):
        return str(self.reason)

class Server(object, logger.Loggable):
    log_domain = "core"

    def __init__(self, env, create=False, debug=False, verbosity=logger.LOG_WARNING):
        """
        Initialize the application
        """
        # check runtime dependencies
        try:
            import twisted
            import django
            import xml.etree.ElementTree
            import mutagen
            import setuptools
        except ImportError, e:
            raise ServerException("%s: make sure the corresponding python package is installed and in your PYTHONPATH." % e)
        # create environment directory if necessary
        if create:
            try:
                os.makedirs(env, 0755)
                os.makedirs(os.path.join(env, 'logs'), 0755)
                os.makedirs(os.path.join(env, 'plugins'), 0755)
                os.makedirs(os.path.join(env, 'media'), 0755)
            except Exception, e:
                raise ServerException("Startup failed: couldn't create directory %s (%s)" % (env, e.strerror))
        # verify that environment directory exists and is sane
        if not os.access(env, os.F_OK):
            raise ServerException("Startup failed: Environment directory %s doesn't exist." % env)
        if not os.access(env, os.R_OK):
            raise ServerException("Startup failed: %s is not readable by Higgins." % env)
        if not os.access(env, os.W_OK):
            raise ServerException("Startup failed: %s is not writable by Higgins." % env)
        if not os.access(env, os.X_OK):
            raise ServerException("Startup failed: %s is not executable by Higgins." % env)
        # set HIGGINS_DIR and DATABASE name
        site_settings['HIGGINS_DIR'] = env
        site_settings['DATABASE_NAME'] = os.path.join(env, "database.dat")
        # if debug flag is specified, then don't request to daemonize and log to stdout
        if debug:
            self.daemonize = False
            self.observer = logger.StdoutObserver(colorized=True)
        # otherwise daemonize and log to logs/higgins.log
        else:
            self.daemonize = True
            self.observer = logger.LogfileObserver(LogFile('higgins.log', os.path.join(env, 'logs')))
        self.observer.start()
        self.log_debug("Higgins version is %s" % VERSION)
        if create:
            self.log_debug("created new environment in " + env)
        # set pid file
        self._pidfile = os.path.join(env, "higgins.pid")
        if os.path.exists(self._pidfile):
            try:
                f = open(self._pidfile)
                pid = int(f.read())
                f.close()
            except Exception, e:
                self.log_error("failed to parse PID file '%s': %s" % (self._pidfile, e))
            else:
                self.log_error("Startup failed: another instance is already running with PID %i" % pid)
            raise ServerException("failed to start Higgins")
        # we import conf after parsing options, but before syncing the db tables
        from higgins.conf import conf
        # create db tables if necessary
        django_admin_command('syncdb')
        # importing higgins.loader implicitly loads plugins
        import higgins.loader
        # start the core service
        #from twisted.application import service
        #self.app = service.Application("Higgins")
        from higgins.core.service import core_service
        #core_service.setServiceParent(self.app)
        core_service.startService()

    def run(self):
        """
        Pass control of the application to twisted
        """
        try:
            open(self._pidfile, 'wb').write(str(os.getpid()))
        except Exception, e:
            self.log_error("failed to create PID file '%s': %s" % (self._pidfile, e))
            raise ServerException("failed to create PID file")
        try:
            # pass control to reactor
            from twisted.internet import reactor
            self.log_debug("Server.run(): starting reactor")
            reactor.run()
            self.log_debug("Server.run(): returned from reactor")
            self.stop()
            self.log_debug("Server.run(): returned from self.stop()")
        finally:
            self._removePID()
            self.observer.stop()

    def stop(self):
        """
        Stop the twisted reactor
        """
        self.log_debug("Server.stop(): stopping Higgins")
        from higgins.core.service import core_service
        if core_service.running:
            core_service.stopService()
            self.log_debug("Server.stop(): stopped core service")
        from twisted.internet import reactor
        if reactor.running:
            reactor.stop()
            self.log_debug("Server.stop(): stopped reactor")
        # save configuration settings
        from higgins.conf import conf
        conf.flush()
        self.log_debug("Server.stop(): Higgins is stopped")

    def _removePID(self):
        try:
            os.unlink(self._pidfile)
        except Exception, e:
            self.log_warning("failed to remove PID file '%s': %s" % (self._pidfile, e))

class ServerOptions(usage.Options):
    optFlags = [
        ["create", "c", None],
        ["debug", "d", None],
    ]

    def __init__(self):
        usage.Options.__init__(self)
        self['create'] = False
        self['verbosity'] = logger.LOG_WARNING 
        self['debug'] = False

    def opt_verbose(self):
        if self['verbosity'] < logger.LOG_DEBUG2:
            self['verbosity'] = self['verbosity'] + 1
    opt_v = opt_verbose

    def opt_quiet(self):
        if self['verbosity'] > logger.LOG_FATAL:
            self['verbosity'] = self['verbosity'] - 1
    opt_q = opt_quiet

    def parseArgs(self, env):
        self['env'] = env

    def opt_help(self):
        print "Usage: %s [OPTION]... ENV" % os.path.basename(sys.argv[0])
        print ""
        print "  -c,--create        Create the environment if necessary"
        print "  -d,--debug         Run in the foreground, and log to stdout"
        print "  -q                 Log errors only (-qq to log nothing)"
        print "  -v                 Increase logging (up to -vvv)"
        print "  --help             Display this help"
        print "  --version          Display the version"
        sys.exit(0)

    def opt_version(self):
        print "Higgins version " + VERSION
        sys.exit(0)

def run_application():
    """
    This is the entry point for running Higgins from the higgins-media-server script,
    which is generated at build time by setuptools.
    """
    # parse options
    o = ServerOptions()
    try:
        o.parseOptions(sys.argv[1:])
    except usage.UsageError, e:
        print "Error parsing options: %s" % e
        print ""
        print "Try %s --help for usage information." % os.path.basename(sys.argv[0])
        sys.exit(1)
    except Exception, e:
        print "%s, exiting" % e
        sys.exit(1)
    # initialize the server
    if o['debug']:
        verbosity = logger.LOG_DEBUG2
    else:
        verbosity = o['verbosity']
    server = Server(o['env'], create=o['create'], debug=o['debug'], verbosity=verbosity)
    # fork into the background
    if server.daemonize:
        if os.fork():
            os._exit(0)
        null = os.open('/dev/null', os.O_RDWR)
        for i in range(3):
            os.dup2(null, i)
        os.close(null)
    # run the server
    try:
        server.run()
        sys.exit(0)
    except:
        sys.exit(1)
