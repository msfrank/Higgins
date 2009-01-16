from logging import Loggable
from django.core.management import call_command
from twisted.python import usage

class Application(Loggable):
    log_domain = "core"

    def __init__(self, options=[]):
        """
        Initialize the application
        """
        # parse options
        class HigginsOptions(usage.Options):
            optFlags = [
                ["debug", "d", "Run Higgins in the foreground, and log everything to stdout"],
            ]
            optParameters = [
                ["uid", "u", None, "The UID the process should run under (must be root)"],
                ["gid", "g", None, "The UID the process should run under (must be root)"],
            ]
        o = HigginsOptions()
        try:
            o.parseOptions(options)
        except usage.UsageError, e:
            raise e
        # we import conf after parsing options, but before syncing the db tables
        from higgins.conf import conf
        # create db tables if necessary
        call_command('syncdb')
        # create the parent service
        from twisted.application import service
        self.app = service.Application("Higgins", uid=o['uid'], gid=o['gid'])
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
