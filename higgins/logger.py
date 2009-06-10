# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from time import ctime
import traceback
from twisted.python import log, logfile, util

LOG_FATAL = 0
LOG_ERROR = 1
LOG_WARNING = 2
LOG_INFO = 3
LOG_DEBUG = 4
LOG_DEBUG2 = 5

LEVELS = ['FATAL','ERROR','WARNING','info','debug','debug2']

class Loggable:
    log_domain = "default"
    def log_fatal(self, reason):
        log.msg(reason, level=LOG_FATAL, domain=self.log_domain)
    def log_error(self, reason):
        log.msg(reason, level=LOG_ERROR, domain=self.log_domain)
    def log_warning(self, reason):
        log.msg(reason, level=LOG_WARNING, domain=self.log_domain)
    def log_info(self, reason):
        log.msg(reason, level=LOG_INFO, domain=self.log_domain)
    def log_debug(self, reason):
        log.msg(reason, level=LOG_DEBUG, domain=self.log_domain)
    def log_debug2(self, reason):
        log.msg(reason, level=LOG_DEBUG2, domain=self.log_domain)

class CommonObserver(log.DefaultObserver):
    def _formatMessage(self, params):
        level = params.get('level', LOG_DEBUG)
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
    def __init__(self, f, verbosity=LOG_WARNING):
        self.verbosity = verbosity
        self.write = f.write
        self.flush = f.flush

    def _emit(self, params):
        level = params.get('level', LOG_DEBUG)
        if level > self.verbosity:
            return
        msg = self._formatMessage(params) + '\r\n'
        util.untilConcludes(self.write, msg)
        util.untilConcludes(self.flush)

class StdoutObserver(CommonObserver):
    def __init__(self, colorized=False, verbosity=LOG_WARNING):
        self.verbosity = verbosity
        if colorized:
            self.START_RED = '\033[1;31m'
            self.START_YELLOW = '\033[1;33m'
            self.END = '\033[0m'
        else:
            self.START_RED = ''
            self.START_YELLOW = ''
            self.END = ''

    def _emit(self, params):
        level = params.get('level', LOG_DEBUG)
        if level > self.verbosity:
            return
        msg = self._formatMessage(params)
        if level < LOG_WARNING:
            print self.START_RED + msg + self.END
            print traceback.print_exc()
        elif level == LOG_WARNING:
            print self.START_YELLOW + msg + self.END
        else:
            print msg
