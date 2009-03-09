# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from higgins.core.models import Artist, Album, Song, Genre, Tag

def index(request):
    return render_to_response('templates/front.t', {})
