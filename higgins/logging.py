from twisted.python import log, logfile
from twisted.application import service
from time import ctime

def log_handler(params):
    try:
        level = params.get('level', 'debug')
        time_t = params.get('time', None)
        if time_t:
            time = ctime(time_t)
        else:
            time = ''
        print "[%s] %s: %s" % (level, time, ''.join(params['message']))
    except Exception, e:
        print "[error]: failed to log message: %s (params was %s)" % (e, params)

log.addObserver(log_handler)

def log_fatal(reason):
    log.msg(reason, level="fatal")

def log_error(reason):
    log.msg(reason, level="error")

def log_warn(reason):
    log.msg(reason, level="warning")

def log_info(reason):
    log.msg(reason, level="info")

def log_debug(reason):
    log.msg(reason, level="debug")
