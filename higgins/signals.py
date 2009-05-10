# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from twisted.internet.defer import Deferred
from higgins.logger import Loggable

class SignalDisconnected(Exception):
    pass

class Signal(object, Loggable):
    log_domain = "signal"

    def __init__(self):
        self.receivers = {}

    def matches(self, kwds):
        """
        Override this method in your signal subclass if you want to do keyword
        matching of signal receivers.  If you don't override this method, then
        all receivers will match when the signal is fired.
        """
        return True

    def connect(self, **kwds):
        """Connect to a signal.  Returns a deferred."""
        d = Deferred()
        d.kwds = kwds
        self.receivers[d] = d
        return d

    def _onDisconnect(self, failure):
        pass

    def disconnect(self, d):
        """Disconnect a receiver from a signal."""
        if d in self.receivers:
            d.addErrback(self._onDisconnect)
            d.errback(SignalDisconnected())
            del self.receivers[d]

    def signal(self, result):
        """Signal all registered receivers."""
        self.log_debug("signaling receivers")
        for d in self.receivers.values():
            if self.matches(d.kwds):
                d.callback(result)
                del self.receivers[d]
