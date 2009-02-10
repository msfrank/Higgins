# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see the COPYING
# file or view it at http://www.gnu.org/licenses/lgpl-2.1.html

__import__('pkg_resources').declare_namespace(__name__)

import sys, pwd, grp, os
from django.core.management import call_command as django_admin_command
from twisted.python import usage
from higgins.logging import Loggable
from higgins.site_settings import site_settings

class HigginsOptions(usage.Options):
    optFlags = [
        ["create", "c", "Create the environment if necessary"],
        ["debug", "d", "Run Higgins in the foreground, and log everything to stdout"],
    ]
    optParameters = [
        ["user", "u", None, "The user the process should run under (must be root)"],
        ["group", "g", None, "The group the process should run under (must be root)"],
    ]

    def parseArgs(self, env):
        self['env'] = env

    def postOptions(self):
        if self['debug']:
            print "Debugging enabled"
        # convert user name to UID
        if self['user']:
            try:
                db = pwd.getpwnam(self['user'])
                self['user'] = db[2]
            except KeyError:
                raise Exception("Error parsing options: Unknown user '%s'" % self['user'])
        # convert group name to GID
        if self['group']:
            try:
                db = grp.getgrnam(self['group'])
                self['group'] = db[2]
            except KeyError:
                raise Exception("Error parsing options: Unknown group '%s'" % self['group'])
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
        print "  -u,--user USER     The user the process should run under (must be root)"
        print "  -g,--group GROUP   The group the process should run under (must be root)"
        print "  -d,--debug         Run in the foreground, and log everything to stdout"
        print "  --help"
        print "  --version"
        sys.exit(0)

    def opt_version(self):
        print "Higgins version 0.1"
        sys.exit(0)

class Application(Loggable):
    log_domain = "startup"

    def __init__(self, options=[]):
        """
        Initialize the application
        """
        # check dependencies
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
        # parse options
        o = HigginsOptions()
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
        # check for pid file
        self._pidfile = os.path.join(o['env'], "higgins.pid")
        if os.path.exists(self._pidfile):
            try:
                f = open(self._pidfile)
                pid = int(f.read())
                f.close()
            except Exception, e:
                self.log_warning("failed to parse PID file '%s': %s" % (self._pidfile, e))
            else:
                self.log_error("failed to start Higgins: another instance is already running with PID %i" % pid)
                sys.exit(1)
        else:
            try:
                open(self._pidfile, 'wb').write(str(os.getpid()))
            except Exception, e:
                self.log_error("failed to create PID file '%s': %s" % (self._pidfile, e))
        # this logic in enclosed in a try-except block so the _removePID method
        # will get called if we error out.  we re-raise the exception so we can
        # catch it in the run_application function.
        try:
            # we import conf after parsing options, but before syncing the db tables
            from higgins.conf import conf
            # create db tables if necessary
            django_admin_command('syncdb')
            # importing higgins.loader implicitly loads plugins
            import higgins.loader
            # start the core service
            from twisted.application import service
            self.app = service.Application("Higgins", uid=o['user'], gid=o['group'])
            from core import core_service
            core_service.setServiceParent(self.app)
            core_service.startService()
            # start the UPnP service
            #from higgins.upnp import UPnPService
            #upnp_service = UPnPService()
            #upnp_service.setServiceParent(self.app)
            #upnp_service.startService()
        except Exception, e:
            self._removePID()
            raise e

    def run(self):
        """
        Pass control of the application to twisted
        """
        try:
            from twisted.internet import reactor
            reactor.run()
            # save configuration settings
            from higgins.conf import conf
            conf.flush()
            self.log_debug("higgins is exiting")
        finally:
            self._removePID()

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
    Application(sys.argv[1:]).run()
