# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from time import ctime
import traceback
from twisted.python import log, logfile, util

LEVELS = ['FATAL','ERROR','WARNING','info','debug','debug2']

class Loggable:
    log_domain = "default"
    def log_fatal(self, reason):
        log.msg(reason, level=0, domain=self.log_domain)
    def log_error(self, reason):
        log.msg(reason, level=1, domain=self.log_domain)
    def log_warning(self, reason):
        log.msg(reason, level=2, domain=self.log_domain)
    def log_info(self, reason):
        log.msg(reason, level=3, domain=self.log_domain)
    def log_debug(self, reason):
        log.msg(reason, level=4, domain=self.log_domain)
    def log_debug2(self, reason):
        log.msg(reason, level=5, domain=self.log_domain)

class CommonObserver(log.DefaultObserver):
    def _formatMessage(self, params):
        level = params.get('level', 4)
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
        return "%s [%s] %s: %s" % (time, domain, LEVELS[level], ''.join(params['message']))

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
        if level < 2:
            print self.START_RED + msg + self.END
            print traceback.print_exc()
        elif level == 2:
            print self.START_YELLOW + msg + self.END
        else:
            print msg
