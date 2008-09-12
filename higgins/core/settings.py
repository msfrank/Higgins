from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from higgins.logging import log_debug, log_error
from higgins.conf import conf
from higgins.loader import configs

def front(request):
    return render_to_response('settings-front.t')

def configure(request, module):
    # if there is no configurator named module, then return a 404
    try:
        config_factory = configs[module]
    except:
        raise Http404
    # if method is GET, then return a prefilled form
    if request.method == 'GET':
        config = config_factory(conf)
        return render_to_response('settings-service.t', {'config': config})
    # otherwise method is POST, parse the form data
    config = config_factory(request.POST)
    if config.is_valid():
        new_values = {}
        for name in config.fields.keys():
            new_values[name] = config.clean_data[name]
        conf.set(**new_values)
    else:
        log_debug("config form is not valid")
    return render_to_response('settings-service.t', {'config': config})

def configure_services(request):
    from higgins.loader import services
    service_items = []
    # if method is GET, then display the form
    if request.method == 'GET':
        for name,service in services.items():
            item = { 'name': name, 'service': service, 'config': configs.get(name, None) }
            service_items.append(item)
        return render_to_response('settings-services.t', {'service_items': service_items })
    # if method is POST, then validate the form
    enabled_services = []
    for name,service in services.items():
        is_enabled = request.POST.get(name, None)
        if not is_enabled == None:
            if service.running == 0:
                service.startService()
                log_debug ("started service %s" % name)
            enabled_services.append(name)
        elif not service.running == 0:
            service.stopService()
            log_debug ("stopped service %s" % name)
        item = { 'name': name, 'service': service, 'config': configs.get(name, None) }
        service_items.append(item)
    conf.set(ENABLED_SERVICES=enabled_services)
    return render_to_response('settings-services.t', {'service_items': service_items })
