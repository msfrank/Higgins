# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^/?$', 'higgins.core.front.index'),
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^browse/$', 'higgins.core.browser.index'),
    (r'^browse/byartist/(?P<artist_id>\d+)/$', 'higgins.core.browser.byartist'),
    (r'^browse/bysong/(?P<song_id>\d+)/$', 'higgins.core.browser.bysong'),
    (r'^browse/byalbum/(?P<album_id>\d+)/$', 'higgins.core.browser.byalbum'),
    (r'^browse/bygenre/(?P<genre_id>\d+)/$', 'higgins.core.browser.bygenre'),
    (r'^browse/artists/$', 'higgins.core.browser.artists'),
    (r'^browse/genres/$', 'higgins.core.browser.genres'),
    (r'^browse/tags/$', 'higgins.core.browser.tags'),
    (r'^search/$', 'higgins.core.search.index'),
    (r'^settings/plugins/$', 'higgins.core.settings.list_plugins'),
    (r'^settings/plugins/(?P<name>\w+)/$', 'higgins.core.settings.configure_plugin'),
    (r'^settings/$', 'higgins.core.settings.front'),
    (r'^settings/(?P<name>\w+)/$', 'higgins.core.settings.configure_toplevel'),
)
