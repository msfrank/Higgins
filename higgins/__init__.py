__import__('pkg_resources').declare_namespace(__name__)

from logging import Loggable
from site_settings import site_settings
from django.core.management import call_command as django_admin_command
from twisted.python import usage
import sys, pwd, grp, os

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
                raise Exception("Unknown user '%s'" % self['user'])
        # convert group name to GID
        if self['group']:
            try:
                db = grp.getgrnam(self['group'])
                self['group'] = db[2]
            except KeyError:
                raise Exception("Unknown group '%s'" % self['group'])
        # create environment directory if necessary
        if self['create']:
            pass
        # verify that environment directory exists and is sane
        else:
            pass
        site_settings['HIGGINS_DIR'] = self['env']
        site_settings['DATABASE_NAME'] = os.path.join(self['env'], "database.dat")

    def opt_help(self):
        print "Usage: %s [OPTION]... ENV" % sys.argv[0]
        print ""
        print "  -c,--create        Create the environment if necessary"
        print "  -u,--user USER     The user the process should run under (must be root)"
        print "  -g,--group GROUP   The group the process should run under (must be root)"
        print "  -d,--debug         Run in the foreground, and log everything to stdout"
        print "  -h,--help"
        print "  -v,--version"
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
        o = HigginsOptions()
        try:
            o.parseOptions(options)
        except Exception, e:
            print "Error parsing options: %s" % e
            print ""
            print "Try %s --help for usage information." % sys.argv[0]
            sys.exit(0)

        # we import conf after parsing options, but before syncing the db tables
        from higgins.conf import conf
        # create db tables if necessary
        django_admin_command('syncdb')
        # create the parent service
        from twisted.application import service
        self.app = service.Application("Higgins", uid=o['user'], gid=o['group'])
        # start the core service
        from higgins.core import CoreService
        core_service = CoreService()
        core_service.setServiceParent(self.app)
        core_service.startService()
        try:
            from higgins.loader import services
            # load enabled services
            enabled_services = conf.get("ENABLED_SERVICES", [])
            for service_name in enabled_services:
                service = services[service_name]
                service.setServiceParent(self.app)
                service.startService()
                self.log_debug("started service '%s'" % service_name)
            self.log_debug ("finished loading services")
        except Exception, e:
            raise e

    def run(self):
        """
        Pass control of the application to twisted
        """
        from twisted.internet import reactor
        reactor.run()
        # save configuration settings
        from higgins.conf import conf
        conf.flush()
        self.log_debug("higgins is exiting")

def run_application():
    import sys
    Application(sys.argv[1:]).run()

