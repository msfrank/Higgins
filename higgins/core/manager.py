# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import os, tempfile
from higgins.http import resource, http_headers
from higgins.http.http import Response as HttpResponse
from higgins.core.models import File, Artist, Album, Song, Genre
from higgins.core.postable_resource import PostableResource
from higgins.core.logger import CoreLogger

class UniqueFile:
    def __init__(self, filename, mimetype='application/octet-stream'):
        self.mimetype = mimetype
        self._fd,self.path = tempfile.mkstemp(prefix=filename + '.', dir='.')
    def write(self, data):
        os.write(self._fd, data)
    def close(self):
        os.close(self._fd)
        del(self._fd)

class CreateCommand(PostableResource, CoreLogger):
    def acceptFile(self, headers):
        content_disposition = headers.getHeader('content-disposition')
        if 'filename' in content_disposition.params:
            filename = content_disposition.params['filename']
        else:
            filename = "file"
        content_type = headers.getHeader('content-type')
        if isinstance(content_type, http_headers.MimeType):
            mimetype = content_type.mediaType + '/' + content_type.mediaSubtype
        else:
            mimetype = 'application/octet-stream'
        file = UniqueFile(filename, mimetype)
        self.log_debug("acceptFile: created new unique file %s" % file.path);
        return file

    def render(self, request):
        try:
            # title is required
            title = request.post.get('title', None)
            if title == None:
                return HttpResponse(400, stream="Missing required form item 'title")

            is_local = request.args.get('is_local', None)
            # process in local mode
            if not is_local == None:
                local_path = request.post.get('local_path', None)
                if local_path == None:
                    return HttpResponse(400, stream="Missing required form item 'local_path'")
                mimetype = request.post.get('mimetype', None)
                if mimetype == None:
                    return HttpResponse(400, stream="Missing required form item 'mimetype'")
                # verify that file exists at local_path
                try:
                    s = os.stat(local_path)
                except:
                    return HttpResponse(400, stream="Failed to stat() local file %s" % local_path)
                file = File(path=local_path, mimetype=mimetype, size=s.st_size)
                file.save()
            else:
                nfiles = len(request.files)
                if nfiles == 0:
                    return HttpResponse(400, stream="Not local mode and no file specified")
                if nfiles > 1:
                    return HttpResponse(400, stream="More than one file specified")
                posted = request.files[0]
                try:
                    s = os.stat(posted.path)
                except:
                    return HttpResponse(400, stream="Failed to stat() local file %s" % local_path)
                file = File(path=posted.path, mimetype=posted.mimetype, size=s.st_size)
                file.save()
                self.log_debug("CreateCommand: created new file %s" % posted.path)

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

            self.log_debug("successfully added new song '%s'" % title)
            return HttpResponse(200, stream="success!")

        except Exception, e:
            self.log_debug("CreateCommand failed: %s" % e)
            return HttpResponse(500, stream="Internal Server Error")

class UpdateCommand(resource.Resource, CoreLogger):
    def render(self, request):
        return HttpResponse(404)

class DeleteCommand(resource.Resource, CoreLogger):
    def render(self, request):
        return HttpResponse(404)

class ManagerResource(resource.Resource, CoreLogger):
    def locateChild(self, request, segments):
        if segments[0] == "create":
            return CreateCommand(), []
        if segments[0] == "update":
            return UpdateCommand(), []
        if segments[0] == "delete":
            return DeleteCommand(), []
        return None, []
