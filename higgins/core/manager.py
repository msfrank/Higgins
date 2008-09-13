from twisted.web2 import http, resource
from higgins.core.models import File, Artist, Album, Song, Genre
from higgins.core.postable_resource import PostableResource
from higgins.logging import log_debug, log_error

class CreateCommand(PostableResource):
    def acceptFile(self, headers):
        log_debug("[core]: acceptFile");
        log_debug("[core]: acceptFile: headers=%s" % headers)
        return None

    def render(self, request):
        log_debug("[core] CreateCommand: render")
        return http.Response(200, stream="success");
        try:
            # title is required
            title = request.post.get('title', None)
            if title == None:
                raise http.Response(400, stream="Missing required form item 'title")

            # process in local mode
            is_local = request.args.get('is_local', None)
            if not is_local == None:
                local_path = request.post.get('local_path', None)
                if local_path == None:
                    raise http.Response(400, stream="Missing required form item 'local_path'")
                mimetype = request.post.get('mimetype', None)
                if mimetype == None:
                    raise http.Response(400, stream="Missing required form item 'mimetype'")
                # verify that file exists at local_path
                from os import stat
                try:
                    s = stat(local_path)
                except:
                    raise http.Response(400, stream="Failed to stat() local file %s" % local_path)
                file = File(path=local_path, mimetype=mimetype, size=s.st_size)
                file.save()

#            if not len(request.FILES.lists()) == 1:
#                resp = HttpResponse()
#                resp.status_code = 400
#                return resp
#            context = {}
#            context['method'] = 'create'
#            context['filename'] = request.FILES['file']['filename']
#            context['content-type'] = request.FILES['file']['content-type']
#            params = request.POST.lists()

            # create or get the artist object
            value = request.post.get('artist', None)
            if value:
                artist,created = Artist.objects.get_or_create(name=value)
            else:
                artist,created = Artist.objects.get_or_create(name="")
            artist.save()

            # create or get the genre object
            value = request.post.get('genre', None)
            if value:
                genre,created = Genre.objects.get_or_create(name=value)
            else:
                genre,created = Genre.objects.get_or_create(name="")
            genre.save()

            # create or get the album object
            value = request.post.get('album', None)
            if value:
                album,created = Album.objects.get_or_create(name=value, artist=artist, genre=genre)
            else:
                album,created = Album.objects.get_or_create(name="", artist=artist, genre=genre)
            album.save()

            # create the song object
            song = Song(name=title, album=album, artist=artist, file=file)
            value = request.post.get('track', None)
            if value:
                song.track_number = int(value)
            value = request.post.get('length', None)
            if value:
                song.duration = int(value)
            song.save()

            log_debug("[core]: successfully added new song '%s'" % title)
            return http.Response(200, stream="success!")

        except http.Response, r:
            return r

class UpdateCommand(resource.Resource):
    def render(self, request):
        return http.Response(404)

class DeleteCommand(resource.Resource):
    def render(self, request):
        return http.Response(404)

class ManagerResource(resource.Resource):
    def locateChild(self, request, segments):
        if segments[0] == "create":
            return CreateCommand(), []
        if segments[0] == "update":
            return UpdateCommand(), []
        if segments[0] == "delete":
            return DeleteCommand(), []
        return None, []
