# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from django.http import Http404
from higgins.core.logger import logger

def show(request, name, core_service):
    # if there is no plugin named module, then return a 404
    try:
        plugin = core_service._plugins[name]
    except KeyError:
        logger.log_error("couldn't find plugin %s" % name)
        raise Http404
    except Exception, e:
        logger.log_error("couldn't display page for plugin %s: %s" % (name, e))
        raise Http500
    if plugin.pages is None:
        logger.log_error("plugin %s doesn't have any frontend pages" % name)
        raise Http404
    # split path into segments, remove any empty values
    segments = [part for part in request.path.split('/') if part != '']
    # remove /view/<frontend>/
    segments = segments[2:]
    # find the page associated with the url
    if segments == []:
        if callable(plugin.pages):
            return plugin.pages(request)
        if isinstance(plugin.pages, dict) and '' in plugin.pages and callable(plugin.pages['']):
            return plugin.pages[''](request)
        raise Http404
    def find_page(segments, pages):
        try:
            part = segments.pop(0)
            page = pages[part]
            if segments == []:
                if callable(page):
                    return page
            else:
                if isinstance(page, dict):
                    return find_page(segments, page)
        except:
            pass
        raise Http404
    page = find_page(segments, plugin.pages)
    return page(request)

