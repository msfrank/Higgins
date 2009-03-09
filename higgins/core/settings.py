# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from higgins.conf import conf
from higgins.core.logger import logger

def front(request, core_service):
    return render_to_response('settings-front.t', {'config_items': core_service._config_items.values() })

def list_plugins(request, core_service):
    # if method is GET, then display the form
    if request.method == 'GET':
        return render_to_response('settings-plugins.t',
            {'plugins': core_service._plugins.values(), 'config_items': core_service._config_items.values() }
            )
    # if method is POST, then validate the form
    for name,plugin in core_service._plugins.items():
        do_enable = request.POST.get(name, False)
        is_enabled = core_service.pluginIsEnabled(name)
        if do_enable and not is_enabled:
                core_service.enablePlugin(name)
        elif not do_enable and is_enabled:
            core_service.disablePlugin(name)
    return render_to_response('settings-plugins.t',
        {'plugins': core_service._plugins.values(), 'config_items': core_service._config_items.values() }
        )

def configure_toplevel(request, core_service, name):
    # if there is no configurator named module, then return a 404
    try:
        factory = core_service._config_items[name]['config']
    except:
        raise Http404
    # if method is GET, then return a prefilled form
    if request.method == 'GET':
        config = factory()
        return render_to_response('settings-plugin.t',
            { 'config': config, 'config_items': core_service._config_items.values() }
            )
    # otherwise method is POST, parse the form data
    config = factory(request.POST)
    return render_to_response('settings-plugin.t',
        { 'config': config, 'config_items': core_service._config_items.values() }
        )

def configure_plugin(request, core_service, name):
    # if there is no plugin named module, then return a 404
    try:
        plugin = core_service._plugins[name]
        if plugin.configs is None:
            logger.log_error("plugin %s doesn't have a Configurator" % name)
            raise Http404 
    except KeyError:
        logger.log_error("couldn't find plugin %s" % name)
        raise Http404
    except Exception, e:
        logger.log_error("couldn't configure plugin %s: %s" % (name, e))
        raise Http500
    # if method is GET, then return a prefilled form
    if request.method == 'GET':
        config = plugin.configs()
        return render_to_response('settings-plugin.t',
            { 'config': config, 'config_items': core_service._config_items.values() }
            )
    # otherwise method is POST, parse the form data
    config = plugin.configs(request.POST)
    return render_to_response('settings-plugin.t',
        { 'config': config, 'config_items': core_service._config_items.values() }
        )
