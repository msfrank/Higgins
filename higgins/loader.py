from higgins.conf import conf
from pkg_resources import Environment, working_set, resource_string
from logging import Loggable
from django.template import TemplateDoesNotExist
import os

class LoaderLogger(Loggable):
    log_domain = "loader"
logger = LoaderLogger()

def load_template_source(template_name, template_dirs=None):
    """
    Loads templates for django from Python eggs via pkg_resource.resource_string.
    """
    if resource_string is not None:
        pkg_name = 'templates/' + template_name
        try:
            charset = conf.get('FILE_CHARSET', 'ISO-8859-1')
            return (resource_string('higgins.data', pkg_name).decode(charset), 'higgins.data:%s' % pkg_name)
        except Exception, e:
            logger.log_warning("failed to load template '%s': %s" % (template_name,e))
    raise TemplateDoesNotExist, template_name
load_template_source.is_usable = True

plugins = []
services = {}
configs = {}
frontends = {}
devices = {}

try:
    import higgins
    plugins_dir = os.path.join(conf.get("HIGGINS_DIR"), "plugins")
    working_set.add_entry(plugins_dir)
    env = Environment([plugins_dir,])
    plugins,errors = working_set.find_plugins(env)
    # load plugin eggs
    for p in plugins:
        working_set.add(p)
        logger.log_debug("loaded plugin '%s'" % p)
    for e in errors:
        logger.log_error("failed to load plugin '%s'" % e)
    # load all discovered services
    for ep in working_set.iter_entry_points('higgins.service'):
        try:
            factory = ep.load()
            issubclass(factory, higgins.service.Service)
            service = factory()
            services[ep.name] = service
            logger.log_debug("loaded service '%s'" % ep.name)
        except Exception, e:
            logger.log_error("failed to load service '%s': %s" % (ep.name, e))
    # load all discovered configs
    for ep in working_set.iter_entry_points('higgins.core.configurator'):
        try:
            factory = ep.load()
            issubclass(factory, higgins.core.configurator.Configurator)
            configs[ep.name] = factory
            logger.log_debug("loaded configurator '%s'" % ep.name)
        except Exception, e:
            logger.log_error("failed to load configurator '%s': %s" % (ep.name, e))
    # load all discovered UPnP devices
    for ep in working_set.iter_entry_points('higgins.upnp.device'):
        try:
            factory = ep.load()
            issubclass(factory, higgins.upnp.device.Device)
            devices[ep.name] = factory
            logger.log_debug("loaded upnp device '%s'" % ep.name)
        except Exception, e:
            logger.log_error("failed to load upnp device '%s': %s" % (ep.name, e))
except Exception, e:
    logger.log_error("plugin loader failure: %s" % e)
    raise e
