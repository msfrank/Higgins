from twisted.python import log, logfile
from time import ctime

class Loggable:
    log_domain = "default"
    def log_fatal(self, reason):
        log.msg(reason, level="FATAL", domain=self.log_domain)
    def log_error(self, reason):
        log.msg(reason, level="ERROR", domain=self.log_domain)
    def log_warn(self, reason):
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
#        if domain == '<none>':
#            print "log_handler: params = %s" % params
        if params.get('printed') == True:
            if params.get('isError') == True:
                domain = "stderr"
            else:
                domain = "stdout"
        if time_t:
            time = ctime(time_t)
        else:
            time = ''
        print "%s [%s] %s: %s" % (time, domain, level, ''.join(params['message']))
    except Exception, e:
        print "%s [default] ERROR: failed to log message: %s (params was %s)" % (time, e, params)

log.addObserver(log_handler)

def log_fatal(domain, reason):
    log.msg(reason, level="FATAL", domain=domain)

def log_error(domain, reason):
    log.msg(reason, level="ERROR", domain=domain)

def log_warn(domain, reason):
    log.msg(reason, level="warning", domain=domain)

def log_info(domain, reason):
    log.msg(reason, level="info", domain=domain)

def log_debug(domain, reason):
    log.msg(reason, level="debug", domain=domain)
