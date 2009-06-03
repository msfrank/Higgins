# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList, maybeDeferred
from higgins.service import Service
from higgins.core import configurator
from higgins.plugins.daap.logger import logger

class DaapConfig(configurator.Configurator):
    pretty_name = "DAAP"
    description = "Configure DAAP sharing"
    SHARE_NAME = configurator.StringSetting("Share Name", "Higgins DAAP Share")

class DaapPrivate(configurator.Configurator):
    REVISION_NUMBER = configurator.IntegerSetting("Revision Number", 1)

from higgins.plugins.daap.commands import DAAPFactory

class DaapService(Service):
    pretty_name = "DAAP"
    description = "Exposes the Higgins media store as a DAAP (iTunes) share"
    configs = DaapConfig()

    def __init__(self):
        try:
            import dbus, avahi
        except ImportError, e:
            raise e
        self.dbus = None
        self.sessions = {}
        self.streams = {}
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
        self.factory = DAAPFactory(self)
        self.listener = reactor.listenTCP(3689, self.factory)
        # tell avahi about our DAAP service
        self.avahi_group.AddService(avahi.IF_UNSPEC,
                                    avahi.PROTO_UNSPEC,
                                    dbus.UInt32(0),
                                    DaapConfig.SHARE_NAME,
                                    "_daap._tcp", 
                                    "",
                                    "",
                                    dbus.UInt16(3689),
                                    avahi.string_array_to_txt_array([
                                        "txtvers=1",
                                        "Machine Name=%s" % DaapConfig.SHARE_NAME,
                                        "Password=false",
                                        "Media Kinds Shared=1"
                                        ])
                                    )
        self.avahi_group.Commit()
        Service.startService(self)
        logger.log_debug("started DAAP service")

    def _doWait(self, result):
        for (didSucceed,value) in result:
            if didSucceed:
                logger.log_debug("deferred succeeded with result %s" % str(value))
            else:
                logger.log_debug("deferred failed with result %s" % str(value.getErrorMessage()))
        logger.log_debug("waiting for DAAP clients to disconnect")
        reactor.callLater(1, self._serviceDone.callback, None)

    def _doStopService(self, result):
        # advertise that the mDNS service has gone away
        self.avahi_group.Reset()
        self.avahi_group.Free()
        self.avahi_group = None
        logger.log_debug("stopped DAAP service")

    def stopService(self):
        # stop listening on the DAAP port
        self.listener.stopListening()
        # create a list of waiting streams
        deferreds = [s.deferred for s in self.streams.values()]
        dl = DeferredList(deferreds + [maybeDeferred(Service.stopService, self)])
        # schedule a second deferred to fire after the streams are (hopefully) closed
        self._serviceDone = Deferred()
        self._serviceDone.addCallback(self._doStopService)
        dl.addCallback(self._doWait)
        # signal each stream to return revision number 0
        for d in deferreds:
            d.callback(0)
        # reset server private data
        self.sessions = {}
        self.streams = {}
        return self._serviceDone
