# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import sys

def installReactor():
    # backup argv then empty sys.argv
    argv = sys.argv
    sys.argv = []
    # now we can safely import gstreamer without it fscking with argv
    import gobject
    import pygst
    pygst.require('0.10')
    import gst
    gobject.threads_init()
    from twisted.internet import glib2reactor
    glib2reactor.install()
    # set argv back
    sys.argv = argv
