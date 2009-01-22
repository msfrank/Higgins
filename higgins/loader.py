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
        log_debug("loader", "loaded plugin '%s'" % p)
    for e in errors:
        log_error("loader", "failed to load plugin '%s'" % e)
    for ep in working_set.iter_entry_points('higgins.plugin.service'):
        factory = ep.load()
        service = factory()
        services[ep.name] = service
    for ep in working_set.iter_entry_points('higgins.plugin.config'):
        configs[ep.name] = ep.load()
except Exception, e:
    log_debug("loader", "plugin loader failure: %s" % e)
    raise e


# Wrapper for loading django templates from higgins.
try:
    from pkg_resources import resource_string
except ImportError:
    resource_string = None

from django.template import TemplateDoesNotExist
from django.conf import settings

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
