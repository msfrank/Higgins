# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from higgins.logger import Loggable

class DAAPLogger(Loggable):
    log_domain = "daap"
logger = DAAPLogger()
