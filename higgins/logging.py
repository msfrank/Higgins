from twisted.python import log, logfile
from time import ctime

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

def log_handler(params):
    try:
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
        if level == 'FATAL' or level == 'ERROR':
            print "\033[1;31m%s [%s] %s: %s\033[0m" % (time, domain, level, ''.join(params['message']))
        elif level == 'warning':
            print "\033[1;33m%s [%s] %s: %s\033[0m" % (time, domain, level, ''.join(params['message']))
        else:
            print "%s [%s] %s: %s" % (time, domain, level, ''.join(params['message']))
    except Exception, e:
        print "\033[1;31m%s [default] ERROR: failed to log message: %s (params was %s)\033[0m" % (time, e, params)

log.addObserver(log_handler)
