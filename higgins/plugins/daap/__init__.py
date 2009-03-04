# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from twisted.internet import reactor
from higgins.service import Service
from higgins.core import configurator
from higgins.plugins.daap.logger import logger

class DaapConfig(configurator.Configurator):
    pretty_name = "DAAP"
    description = "Configure DAAP sharing"
    SHARE_NAME = configurator.StringSetting("Share Name", "Higgins DAAP Share")

class DaapPrivate(configurator.Configurator):
    REVISION_NUMBER = configurator.IntegerSetting("Revision Number", 5)

from higgins.plugins.daap.commands import DAAPFactory

class DaapService(Service):
    pretty_name = "DAAP"
    description = "Exposes the Higgins media store as a DAAP (iTunes) share"
    configs = DaapConfig

    def __init__(self):
        try:
            import dbus, avahi
        except ImportError, e:
            raise e
        self.dbus = None
        Service.__init__(self)

    def startService(self):
        import dbus, avahi
        if self.dbus == None:
            # create the avahi server interface object
            self.dbus = dbus.SystemBus()
            proxy = self.dbus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER)
            self.avahi_server = dbus.Interface(proxy, avahi.DBUS_INTERFACE_SERVER)
        proxy = self.dbus.get_object(avahi.DBUS_NAME, self.avahi_server.EntryGroupNew())
        self.avahi_group = dbus.Interface(proxy, avahi.DBUS_INTERFACE_ENTRY_GROUP)
        # create the DAAP listener
        self.listener = reactor.listenTCP(3689, DAAPFactory())
        # tell avahi about our DAAP service
        self.avahi_group.AddService(avahi.IF_UNSPEC,
                                    avahi.PROTO_UNSPEC,
                                    0,
                                    DaapConfig.SHARE_NAME,
                                    "_daap._tcp", 
                                    "", "", 3689, [])
        self.avahi_group.Commit()
        Service.startService(self)
        logger.log_debug("started DAAP service")

    def stopService(self):
        self.avahi_group.Reset()
        self.avahi_group = None
        self.listener.stopListening()
        logger.log_debug("stopped DAAP service")
        Service.stopService(self)
        return None
