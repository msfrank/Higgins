from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from logger import CoreLogger
from higgins.conf import conf
from higgins.loader import configs,services

logger = CoreLogger()

def get_toplevel_configs():
    config_items = []
    for name,config in configs.items():
        item = { 'name': name, 'config': config }
        config_items.append(item)
    return config_items

def front(request):
    return render_to_response('settings-front.t', {'config_items': get_toplevel_configs() })

def list_services(request):
    service_items = []
    # if method is GET, then display the form
    if request.method == 'GET':
        for name,service in services.items():
            item = { 'name': name, 'service': service }
            logger.log_debug("found service %s, service_config=%s" % (name,str(service.service_config)))
            service_items.append(item)
        return render_to_response('settings-services.t', {'service_items': service_items, 'config_items': get_toplevel_configs() })
    # if method is POST, then validate the form
    enabled_services = []
    for name,service in services.items():
        is_enabled = request.POST.get(name, None)
        if not is_enabled == None:
            if service.running == 0:
                service.startService()
                logger.log_debug ("started service %s" % name)
            enabled_services.append(name)
        elif not service.running == 0:
            service.stopService()
            logger.log_debug ("stopped service %s" % name)
        item = { 'name': name, 'service': service }
        service_items.append(item)
    conf.set(ENABLED_SERVICES=enabled_services)
    return render_to_response('settings-services.t', {'service_items': service_items, 'config_items': get_toplevel_configs() })

def configure(request, module):
    # if there is no configurator named module, then return a 404
    try:
        factory = configs[module]
    except:
        raise Http404
    toplevel_configs = get_toplevel_configs()
    # if method is GET, then return a prefilled form
    if request.method == 'GET':
        config = factory(conf)
        logger.log_debug("config_items: %s" % toplevel_configs)
        return render_to_response('settings-service.t', {'config': config, 'config_items': toplevel_configs })
    # otherwise method is POST, parse the form data
    config = factory(request.POST)
    if config.is_valid():
        new_values = {}
        for name in config.fields.keys():
            new_values[name] = config.cleaned_data[name]
        conf.set(**new_values)
    else:
        logger.log_warning("config form is not valid")
    logger.log_debug("config_items: %s" % toplevel_configs)
    return render_to_response('settings-service.t', {'config': config, 'config_items': toplevel_configs })

def configure_service(request, module):
    # if there is no service named module, then return a 404
    try:
        service = services[module]
        if service.service_config is None:
            raise Http404 
    except:
        raise Http404
    # if method is GET, then return a prefilled form
    if request.method == 'GET':
        config = service.service_config(conf)
        return render_to_response('settings-service.t', {'config': config, 'config_items': get_toplevel_configs() })
    # otherwise method is POST, parse the form data
    config = service.service_config(request.POST)
    if config.is_valid():
        new_values = {}
        for name in config.fields.keys():
            new_values[name] = config.cleaned_data[name]
        conf.set(**new_values)
    else:
        logger.log_debug("config form is not valid")
    return render_to_response('settings-service.t', {'config': config, 'config_items': get_toplevel_configs() })
