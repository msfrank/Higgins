from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.core.urlresolvers import reverse
from higgins.core.models import File, Artist, Album, Song, Genre

def create(request):
    if request.method == 'POST':
        try:
            # title is required
            title = request.POST.get('title', None)
            if title == None:
                resp = HttpResponse("Missing required form item 'title")
                resp.status_code = 400
                return resp

            # process in local mode
            is_local = request.GET.get('is_local', "false")
            if is_local == 'true':
                local_path = request.POST.get('local_path', None)
                if local_path == None:
                    resp = HttpResponse("Missing required form item 'local_path'")
                    resp.status_code = 400
                    return resp
                mimetype = request.POST.get('mimetype', None)
                if mimetype == None:
                    resp = HttpResponse("Missing required form item 'mimetype'")
                    resp.status_code = 400
                    return resp
                # verify that file exists at local_path
                from os import stat
                try:
                    s = stat(local_path)
                except:
                    resp = HttpResponse("Failed to stat() local file %s" % local_path)
                    resp.status_code = 400
                    return resp
                file = File(path=local_path, mimetype=mimetype, size=s.st_size)
                file.save()

            # create or get the artist object
            value = request.POST.get('artist', None)
            if value:
                artist,created = Artist.objects.get_or_create(name=value)
            else:
                artist,created = Artist.objects.get_or_create(name="")
            artist.save()

            # create or get the genre object
            value = request.POST.get('genre', None)
            if value:
                genre,created = Genre.objects.get_or_create(name=value)
            else:
                genre,created = Genre.objects.get_or_create(name="")
            genre.save()

            # create or get the album object
            value = request.POST.get('album', None)
            if value:
                album,created = Album.objects.get_or_create(name=value, artist=artist, genre=genre)
            else:
                album,created = Album.objects.get_or_create(name="", artist=artist, genre=genre)
            album.save()

            # create the song object
            song = Song(name=title, album=album, artist=artist, file=file)
            value = request.POST.get('track', None)
            if value:
                song.track_number = int(value)
            value = request.POST.get('length', None)
            if value:
                song.duration = int(value)
            song.save()

            print "successfully added new song"
            return HttpResponse("success!")
        except Exception, e:
            print "Caught exception: %s" % e

#        if not len(request.FILES.lists()) == 1:
#            resp = HttpResponse()
#            resp.status_code = 400
#            return resp
#        context = {}
#        context['method'] = 'create'
#        context['filename'] = request.FILES['file']['filename']
#        context['content-type'] = request.FILES['file']['content-type']
#        params = request.POST.lists()
#        return HttpResponseRedirect(reverse("ums.manager.views.create_result"))
#    return render_to_response("manager/create.t", {})

def create_result(request):
        return render_to_response("manager/result.t", {'context': context })

def update(request):
    return HttpResponseNotFound

def delete(request):
    return HttpResponseNotFound
