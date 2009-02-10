# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see the COPYING
# file or view it at http://www.gnu.org/licenses/lgpl-2.1.html

__import__('pkg_resources').declare_namespace(__name__)

import sys, pwd, grp, os
from django.core.management import call_command as django_admin_command
from twisted.python import usage
from twisted.python.logfile import LogFile
from higgins.logging import Loggable, StdoutObserver, LogfileObserver
from higgins.site_settings import site_settings

class HigginsOptions(usage.Options):
    optFlags = [
        ["create", "c", "Create the environment if necessary"],
        ["debug", "d", "Run Higgins in the foreground, and log everything to stdout"],
    ]

    def __init__(self, app):
        self.app = app
        usage.Options.__init__(self)
        self['verbose'] = 0

    def opt_verbose(self):
        self['verbose'] = self['verbose'] + 1
    opt_v = opt_verbose

    def parseArgs(self, env):
        self['env'] = env

    def postOptions(self):
        # create environment directory if necessary
        env_dir = self['env']
        if self['create']:
            try:
                os.makedirs(env_dir, 0755)
                os.makedirs(os.path.join(env_dir, 'logs'), 0755)
                os.makedirs(os.path.join(env_dir, 'plugins'), 0755)
                os.makedirs(os.path.join(env_dir, 'media'), 0755)
            except Exception, e:
                raise Exception("Startup failed: couldn't create directory %s (%s)" % (env_dir, e.strerror))
        # verify that environment directory exists and is sane
        if not os.access(env_dir, os.F_OK):
            raise Exception("Startup failed: Environment directory %s doesn't exist." % env_dir)
        if not os.access(env_dir, os.R_OK):
            raise Exception("Startup failed: %s is not readable by Higgins." % env_dir)
        if not os.access(env_dir, os.W_OK):
            raise Exception("Startup failed: %s is not writable by Higgins." % env_dir)
        if not os.access(env_dir, os.X_OK):
            raise Exception("Startup failed: %s is not executable by Higgins." % env_dir)
        # set HIGGINS_DIR and DATABASE name
        site_settings['HIGGINS_DIR'] = self['env']
        site_settings['DATABASE_NAME'] = os.path.join(self['env'], "database.dat")

    def opt_help(self):
        print "Usage: %s [OPTION]... ENV" % sys.argv[0]
        print ""
        print "  -c,--create        Create the environment if necessary"
        print "  -d,--debug         Run in the foreground, and log everything to stdout"
        print "  -v                 Increase verbosity"
        print "  --help"
        print "  --version"
        sys.exit(0)

    def opt_version(self):
        print "Higgins version 0.1"
        sys.exit(0)

class Application(Loggable):
    log_domain = "core"

    def __init__(self, options=[]):
        """
        Initialize the application
        """
        # parse options
        o = HigginsOptions(self)
        try:
            o.parseOptions(options)
        except usage.UsageError, e:
            print "Error parsing options: %s" % e
            print ""
            print "Try %s --help for usage information." % os.path.basename(sys.argv[0])
            sys.exit(1)
        except Exception, e:
            self.log_error("%s" % e)
            sys.exit(1)
        # check runtime dependencies
        try:
            import twisted
            import twisted.web2
            import django
            import xml.etree.ElementTree
            import mutagen
            import setuptools
        except ImportError, e:
            self.log_error("%s: make sure the corresponding python package is installed and in your PYTHONPATH." % e)
            sys.exit(1)
        # if debug flag is specified, then don't request to daemonize and log to stdout
        if o['debug']:
            self.daemonize = False
            self.observer = StdoutObserver()
        # otherwise daemonize and log to logs/higgins.log
        else:
            self.daemonize = True
            self.observer = LogfileObserver(LogFile('higgins.log', os.path.join(o['env'], 'logs')))
        self.observer.start()
        # set pid file
        self._pidfile = os.path.join(o['env'], "higgins.pid")
        if os.path.exists(self._pidfile):
            try:
                f = open(self._pidfile)
                pid = int(f.read())
                f.close()
            except Exception, e:
                self.log_error("failed to parse PID file '%s': %s" % (self._pidfile, e))
                sys.exit(1)
            else:
                self.log_error("failed to start Higgins: another instance is already running with PID %i" % pid)
                sys.exit(1)
        # we import conf after parsing options, but before syncing the db tables
        from higgins.conf import conf
        # create db tables if necessary
        django_admin_command('syncdb')
        # importing higgins.loader implicitly loads plugins
        import higgins.loader
        # start the core service
        from twisted.application import service
        self.app = service.Application("Higgins")
        from core import core_service
        core_service.setServiceParent(self.app)
        core_service.startService()

    def run(self):
        """
        Pass control of the application to twisted
        """
        try:
            open(self._pidfile, 'wb').write(str(os.getpid()))
        except Exception, e:
            self.log_error("failed to create PID file '%s': %s" % (self._pidfile, e))
            return
        try:
            # pass control to reactor
            from twisted.internet import reactor
            reactor.run()
            # save configuration settings
            from higgins.conf import conf
            conf.flush()
            self.log_debug("higgins is exiting")
        finally:
            self._removePID()
            self.observer.stop()

    def _removePID(self):
        try:
            os.unlink(self._pidfile)
        except Exception, e:
            self.log_warning("failed to remove PID file '%s': %s" % (self._pidfile, e))

def run_application():
    """
    This is the entry point for running Higgins from the higgins-media-server script,
    which is generated at build time by setuptools.
    """
    application = Application(sys.argv[1:])
    if application.daemonize:
        if os.fork():
            os._exit(0)
        null = os.open('/dev/null', os.O_RDWR)
        for i in range(3):
            os.dup2(null, i)
        os.close(null)
    application.run()
