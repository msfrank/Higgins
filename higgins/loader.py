from higgins.conf import conf
from pkg_resources import Environment, working_set
from logging import log_debug, log_error

plugins = []
services = {}
configs = {}

try:
    working_set.add_entry(conf.get("PLUGINS_DIR"))
    env = Environment([conf.get("PLUGINS_DIR")])
    plugins,errors = working_set.find_plugins(env)
    for p in plugins:
        working_set.add(p)
        log_debug("loaded plugin '%s'" % p)
    for e in errors:
        log_error("failed to load plugin '%s'" % e)
    for ep in working_set.iter_entry_points('higgins.plugin.service'):
        factory = ep.load()
        service = factory()
        services[ep.name] = service
    for ep in working_set.iter_entry_points('higgins.plugin.config'):
        configs[ep.name] = ep.load()
except Exception, e:
    log_debug("plugin loader failure: %s" % e)
    raise e

