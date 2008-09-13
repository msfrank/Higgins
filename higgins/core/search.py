from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from higgins.core.models import Artist, Album, Song, Genre, Tag

def index(request):
    raise Http404
