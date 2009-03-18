# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

class UPNPError(Exception):
    def __init__(self, code, reason):
        self.code = code
        self.reason = reason
    def __str__(self):
        return "%s (%i)" % (self.reason, self.code)
