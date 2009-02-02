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
    (r'^settings/services/$', 'higgins.core.settings.list_services'),
    (r'^settings/services/(?P<module>\w+)/$', 'higgins.core.settings.configure_service'),
    (r'^settings/$', 'higgins.core.settings.front'),
    (r'^settings/(?P<module>\w+)/$', 'higgins.core.settings.configure'),
)
