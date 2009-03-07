# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import os
from pkg_resources import Environment, working_set, resource_string
from django.template import TemplateDoesNotExist
from higgins.service import Service
from higgins.logger import Loggable
from higgins.conf import conf
from higgins.core.service import core_service

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

try:
    plugins_dir = os.path.join(conf.get("HIGGINS_DIR"), "plugins")
    logger.log_debug("added '%s' to plugin search path" % plugins_dir)
    working_set.add_entry(plugins_dir)
    env = Environment([plugins_dir,])
    plugins,errors = working_set.find_plugins(env)
    # load plugin eggs
    for p in plugins:
        working_set.add(p)
        logger.log_debug("loaded plugin egg '%s'" % p)
    for e in errors:
        logger.log_error("failed to load plugin egg '%s'" % e)
    # load all discovered plugins
    for ep in working_set.iter_entry_points('higgins.plugin'):
        try:
            factory = ep.load()
            if issubclass(factory, Service):
                logger.log_debug("found service plugin '%s'" % ep.name)
                core_service.registerPlugin(ep.name, factory)
            else:
                logger.log_warning("ignoring plugin '%s': unknown plugin type" % ep.name)
        except Exception, e:
            logger.log_error("failed to load plugin '%s': %s" % (ep.name, e))
except Exception, e:
    logger.log_error("plugin loading failed: %s" % e)
    raise e
