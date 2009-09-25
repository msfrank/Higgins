# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

def installGstReactor():
    import gobject
    import pygst
    pygst.require('0.10')
    import gst
    gobject.threads_init()
    from twisted.internet import glib2reactor
    glib2reactor.install()
