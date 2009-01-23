from higgins.conf import conf
from pkg_resources import Environment, working_set, resource_string
from logging import log_debug, log_error
from django.template import TemplateDoesNotExist
import os

def load_template_source(template_name, template_dirs=None):
    """
    Loads templates from Python eggs via pkg_resource.resource_string.
    """
    if resource_string is not None:
        pkg_name = 'templates/' + template_name
        try:
            charset = conf.get('FILE_CHARSET', 'ISO-8859-1')
            return (resource_string('higgins.data', pkg_name).decode(charset), 'higgins.data:%s' % pkg_name)
        except:
            pass
    raise TemplateDoesNotExist, template_name
load_template_source.is_usable = True


plugins = []
services = {}
configs = {}

try:
    plugins_dir = os.path.join(conf.get("HIGGINS_DIR"), "plugins")
    working_set.add_entry(plugins_dir)
    env = Environment([plugins_dir,])
    plugins,errors = working_set.find_plugins(env)
    for p in plugins:
        working_set.add(p)
        log_debug("loader", "loaded plugin '%s'" % p)
    for e in errors:
        log_error("loader", "failed to load plugin '%s'" % e)
    for ep in working_set.iter_entry_points('higgins.plugin.service'):
        factory = ep.load()
        service = factory()
        services[ep.name] = service
        log_debug("loader", "found entry point for higgins.plugin.service: %s" % ep.name)
    for ep in working_set.iter_entry_points('higgins.plugin.config'):
        configs[ep.name] = ep.load()
        log_debug("loader", "found entry point for higgins.plugin.config: %s" % ep.name)
except Exception, e:
    log_debug("loader", "plugin loader failure: %s" % e)
    raise e
