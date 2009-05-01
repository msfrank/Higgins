# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from twisted.internet.defer import Deferred
from higgins.logger import Loggable

class Signal(object, Loggable):
    log_domain = "signal"

    def __init__(self):
        self.receivers = []

    def matches(self, kwds):
        return True

    def connect(self, **kwds):
        d = Deferred()
        d.kwds = kwds
        self.receivers.append(d)
        return d

    def signal(self, result):
        self.log_debug("signaling all receivers")
        for d in self.receivers:
            if self.matches(d.kwds):
                d.callback(result)
        self.receivers = []

