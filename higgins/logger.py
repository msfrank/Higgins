# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from time import ctime
import traceback
from twisted.python import log, logfile, util

class Severity:
    FATAL = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4
    DEBUG2 = 5
    _names = ('FATAL','ERROR','WARNING','info','debug','debug2')
    @classmethod
    def getName(cls, severity):
        try:
            return cls._names[severity]
        except:
            return 'Unknown'

class Loggable:
    log_domain = "default"
    def log_fatal(self, reason):
        log.msg(reason, level=Severity.FATAL, domain=self.log_domain)
    def log_error(self, reason):
        log.msg(reason, level=Severity.ERROR, domain=self.log_domain)
    def log_warning(self, reason):
        log.msg(reason, level=Severity.WARNING, domain=self.log_domain)
    def log_info(self, reason):
        log.msg(reason, level=Severity.INFO, domain=self.log_domain)
    def log_debug(self, reason):
        log.msg(reason, level=Severity.DEBUG, domain=self.log_domain)
    def log_debug2(self, reason):
        log.msg(reason, level=Severity.DEBUG2, domain=self.log_domain)

class IgnoreMessage(Exception):
    pass

class CommonObserver(log.DefaultObserver):
    def _formatMessage(self, params):
        level = params.get('level', Severity.DEBUG2)
        time_t = params.get('time', None)
        domain = params.get('domain', 'twisted')
        if 'interface' in params:
            raise IgnoreMessage()
        if params.get('printed') == True:
            if params.get('isError') == True:
                domain = "stderr"
            else:
                domain = "stdout"
        if time_t:
            time = ctime(time_t)
        else:
            time = ''
        return "%s [%s] %s: %s" % (time, domain, Severity.getName(level), ''.join(params['message']))

class LogfileObserver(CommonObserver):
    def __init__(self, f, verbosity=Severity.WARNING):
        self.verbosity = verbosity
        self.write = f.write
        self.flush = f.flush

    def _emit(self, params):
        try:
            level = params.get('level', Severity.DEBUG)
            if level > self.verbosity:
                return
            msg = self._formatMessage(params) + '\r\n'
            if self.verbosity >= Severity.DEBUG:
                msg += traceback.format_exc()
            util.untilConcludes(self.write, msg)
            util.untilConcludes(self.flush)
        except IgnoreMessage:
            pass

class StdoutObserver(CommonObserver):
    def __init__(self, colorized=False, verbosity=Severity.WARNING):
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
        try:
            level = params.get('level', Severity.DEBUG)
            if level > self.verbosity:
                return
            msg = self._formatMessage(params)
            if level < Severity.WARNING:
                print self.START_RED + msg + self.END
                if self.verbosity >= Severity.DEBUG:
                    print traceback.format_exc()
            elif level == Severity.WARNING:
                print self.START_YELLOW + msg + self.END
            else:
                print msg
        except IgnoreMessage:
            pass
