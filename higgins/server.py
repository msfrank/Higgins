# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import sys, pwd, grp, os, signal
from axiom.store import Store
from twisted.internet import reactor
from twisted.internet.defer import maybeDeferred
from twisted.python import usage
from twisted.python.logfile import LogFile
from higgins.settings import settings
from higgins.db import db
from higgins.loader import plugins
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
        # if debug flag is specified, then don't request to daemonize and log to stdout
        if debug:
            self.daemonize = False
            self.observer = logger.StdoutObserver(colorized=True, verbosity=verbosity)
        # otherwise daemonize and log to logs/higgins.log
        else:
            self.daemonize = True
            self.observer = logger.LogfileObserver(LogFile('higgins.log', os.path.join(env, 'logs')), verbosity=verbosity)
        self.observer.start()
        self.log_info("Higgins version is %s" % VERSION)
        if create:
            self.log_info("created new environment in " + env)
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
        # we load conf after parsing options
        settings.load(os.path.join(env, 'settings.dat'))
        # open the database
        db.open(os.path.join(env, 'database'))
        # load the list of plugins
        plugins.load([os.path.join(env, 'plugins')])

    def _caughtSignal(self, signum, stack):
        self.log_debug("caught signal %i" % signum)
        self.stop()

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
            from higgins.core.service import CoreService
            self._coreService = CoreService()
            # register plugins
            for name,plugin in plugins:
                self._coreService.registerPlugin(name, plugin)
            # start the core service
            self._coreService.startService()
            # pass control to reactor
            self.log_info("starting twisted reactor")
            self._oldsignal = signal.signal(signal.SIGINT, self._caughtSignal)
            reactor.run()
            signal.signal(signal.SIGINT, self._oldsignal)
            self.log_debug("returned from twisted reactor")
            # save configuration settings
            settings.flush()
        finally:
            try:
                os.unlink(self._pidfile)
            except Exception, e:
                self.log_warning("failed to remove PID file '%s': %s" % (self._pidfile, e))
            self.observer.stop()

    def _doStop(self, result):
        self.log_debug("stopped core service")
        self._coreService = None
        reactor.stop()
        self.log_info("stopped twisted reactor")

    def stop(self):
        """
        Stop the twisted reactor
        """
        if not reactor.running:
            raise Exception("Server is not running")
        if not self._coreService.running:
            raise Exception("CoreService is not running")
        # stops everything
        d = maybeDeferred(self._coreService.stopService)
        d.addCallback(self._doStop)

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
    server = Server(o['env'], create=o['create'], debug=o['debug'], verbosity=o['verbosity'])
    # fork into the background
    if server.daemonize:
        if os.fork():
            os._exit(0)
        null = os.open('/dev/null', os.O_RDWR)
        for i in range(3):
            os.dup2(null, i)
        os.close(null)
    # run the server
    server.run()
    sys.exit(0)
