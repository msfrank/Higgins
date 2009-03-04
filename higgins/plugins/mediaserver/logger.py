# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.logging import Loggable

class MediaserverLogger(Loggable):
    log_domain = "mediaserver"
logger = MediaserverLogger()
