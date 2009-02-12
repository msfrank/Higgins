# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from time import ctime
from twisted.python import log, logfile, util

class Loggable:
    log_domain = "default"
    def log_fatal(self, reason):
        log.msg(reason, level="FATAL", domain=self.log_domain)
    def log_error(self, reason):
        log.msg(reason, level="ERROR", domain=self.log_domain)
    def log_warning(self, reason):
        log.msg(reason, level="warning", domain=self.log_domain)
    def log_info(self, reason):
        log.msg(reason, level="info", domain=self.log_domain)
    def log_debug(self, reason):
        log.msg(reason, level="debug", domain=self.log_domain)

class CommonObserver(log.DefaultObserver):
    def _formatMessage(self, params):
        level = params.get('level', 'debug')
        time_t = params.get('time', None)
        domain = params.get('domain', 'twisted')
        if params.get('printed') == True:
            if params.get('isError') == True:
                domain = "stderr"
            else:
                domain = "stdout"
        if time_t:
            time = ctime(time_t)
        else:
            time = ''
        return "%s [%s] %s: %s" % (time, domain, level, ''.join(params['message']))

class LogfileObserver(CommonObserver):
    def __init__(self, f):
        self.write = f.write
        self.flush = f.flush

    def _emit(self, params):
        msg = self._formatMessage(params) + '\r\n'
        util.untilConcludes(self.write, msg)
        util.untilConcludes(self.flush)

class StdoutObserver(CommonObserver):
    def __init__(self, colorized=False):
        if colorized:
            self.START_RED = '\033[1;31m'
            self.START_YELLOW = '\033[1;33m'
            self.END = '\033[0m'
        else:
            self.START_RED = ''
            self.START_YELLOW = ''
            self.END = ''

    def _emit(self, params):
        level = params.get('level', 'debug')
        msg = self._formatMessage(params)
        if level == 'FATAL' or level == 'ERROR':
            print self.START_RED + msg + self.END
            import traceback
            print traceback.print_exc()
        elif level == 'warning':
            print self.START_YELLOW + msg + self.END
        else:
            print msg
