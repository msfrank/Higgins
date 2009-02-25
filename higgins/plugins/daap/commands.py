# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

from twisted.internet import defer, reactor
from higgins.http.channel import HTTPFactory
from higgins.http.server import Site
from higgins.http.http import Response
from higgins.http.resource import Resource
from higgins.http.stream import SimpleStream, FileStream
from higgins.http.http_headers import MimeType
from higgins.core.models import File, Song
from higgins.plugins.daap import DaapConfig, DaapPrivate
from higgins.plugins.daap.codebag import CodeBag, ContentCode
from higgins.plugins.daap.content_codes import content_codes, content_code_str_to_int
from higgins.plugins.daap.logger import logger

x_dmap_tagged = MimeType('application', 'x-dmap-tagged')

class Command(Resource):
    """The base class for a DAAP command."""

    def renderDAAP(self, request):
        """
        This method is invoked for GET requests on this resource.  Subclasses
        should return a CodeBag which is rendered as the response body, or raise
        an Exception if an error occurred.
        """
        raise Exception('Not Implemented')

    def allowedMethods(self):
        # The only allowed method is a GET request.
        return ('GET',)

    def render(self, request):
        # calls the renderDAAP method and returns its result.
        logger.log_debug("%s %s" % (request.method, request.path))
        logger.log_debug(str(request.args))
        try:
            return Response(200, { 'content-type': x_dmap_tagged }, self.renderDAAP(request).render())
        except Exception, e:
            logger.log_error("command failed: %s" % e)
            return Response(400, { 'content-type': MimeType('text','plain') }, str(e))

class ServerInfoCommand(Command):
    def renderDAAP(self, request):
        msrv = CodeBag("msrv")
        msrv.add(ContentCode("mstt", 200))
        msrv.add(ContentCode("mpro", (2,0,0)))  # version 0.2.0.0
        msrv.add(ContentCode("apro", (3,0,0)))  # version 0.3.0.0
        msrv.add(ContentCode("minm", str(DaapConfig.SHARE_NAME)))
        msrv.add(ContentCode("msau", 0))        # authentication method
        msrv.add(ContentCode("mslr", 1))        # login required?
        msrv.add(ContentCode("mstm", 300))      # timeout interval
        msrv.add(ContentCode("msal", 1))        # support auto-logout?
        msrv.add(ContentCode("msup", 1))        # support update?
        msrv.add(ContentCode("mspi", 1))        # support persistent ids
        msrv.add(ContentCode("msex", 1))        # support extensions?
        msrv.add(ContentCode("msbr", 1))        # support browsing?
        msrv.add(ContentCode("msqy", 1))        # support queries?
        msrv.add(ContentCode("msix", 1))        # support indexing?
        msrv.add(ContentCode("msrs", 1))        # support resolve?
        msrv.add(ContentCode("msdc", 1))        # number of databases
        return msrv

class ContentCodesCommand(Command):
    def renderDAAP(self, request):
        mccr = CodeBag("mccr")
        mccr.add(ContentCode("mstt", 200))
        for name,value in content_codes.items():
            mdcl = CodeBag("mdcl")
            mdcl.add(ContentCode("mcnm", content_code_str_to_int(name)))
            mdcl.add(ContentCode("mcna", value[1]))
            mdcl.add(ContentCode("mcty", value[0]))
            mccr.add(mdcl)
        return mccr

class LoginCommand(Command):
    def renderDAAP(self, request):
        mlog = CodeBag("mlog")
        mlog.add(ContentCode("mstt", 200))
        mlog.add(ContentCode("mlid", 1000000))
        return mlog

class UpdateStream(SimpleStream):
    def __init__(self):
        self.deferred = defer.Deferred()
    def read(self):
        logger.log_debug("UpdateStream: waiting on read")
        return self.deferred
    def close(self):
        logger.log_debug("UpdateStream: closed stream")
        self.length = 0

class UpdateCommand(Command):
    def render(self, request):
        logger.log_debug("%s %s" % (request.method, request.path))
        logger.log_debug(str(request.args))
        try:
            # get revision number
            rid = request.args.get('revision-number', ['0'])
            rid = rid[0]
            rid = int(rid)
            logger.log_debug("UpdateCommand: revision-number is %i" % rid)
            # if revision-number is not current revision number
            if not rid == DaapPrivate.REVISION_NUMBER:
                if rid < 0:
                    raise Exception("invalid revision-number %s" % rid)
                # return the current revision number
                mupd = CodeBag("mupd")
                mupd.add(ContentCode("mstt", 200))
                mupd.add(ContentCode("musr", int(DaapPrivate.REVISION_NUMBER)))
                return Response(200, { 'content-type': x_dmap_tagged }, mupd.render())
            # wait forever
            # FIXME: don't just wait forever ;)  actually respond to updates
            return Response(200, { 'content-type': x_dmap_tagged }, UpdateStream())
        except Exception, e:
            logger.log_error("UpdateCommand failed: %s" % e)
            return Response(400, { 'content-type': MimeType('text','plain') }, str(e))


class DatabaseCommand(Command):
    def locateChild(self, request, segments):
        if segments == []:
            return self, []
        dbid = int(segments[0])
        if len(segments) == 1:
            return None, []
        if segments[1] == "items":
            return ListItemsCommand(dbid), segments[1:]
        if segments[1] == "containers":
            return ListPlaylistsCommand(dbid), segments[1:]
        return None, []
    def renderDAAP(self, request):
        avdb = CodeBag("avdb")
        avdb.add(ContentCode("mstt", 200))      # status code
        avdb.add(ContentCode("muty", 1))        # always 0?
        avdb.add(ContentCode("mtco", 1))         # total number of matching records
        avdb.add(ContentCode("mrco", 1))         # total number of records returned
        listing = CodeBag("mlcl")
        record = CodeBag("mlit")
        record.add(ContentCode("miid", 1))                              # database ID
        record.add(ContentCode("mper", 1))                              # database persistent ID
        record.add(ContentCode("minm", str(DaapConfig.SHARE_NAME)))     # db name
        record.add(ContentCode("mimc", len(Song.objects.all())))        # number of db items
        record.add(ContentCode("mctc", 1))                              # container count
        listing.add(record)
        avdb.add(listing)
        return avdb

class ListItemsCommand(Command):
    def __init__(self, dbid):
        self.dbid = dbid
    def locateChild(self, request, segments):
        if len(segments) == 1:
            return self, []
        try:
            s = segments[1].split('.')
            songid = int(s[0])
        except:
            return None, []
        return StreamSongCommand(songid), []
    def renderDAAP(self, request):
        try:
            meta = ''.join(request.args['meta'])
            #log_debug("[daap] ListItemsCommand requesting metadata fields: %s" % meta)
            from content_codes import reverse_table
            for field in meta.split(','):
                try:
                    code = reverse_table[field]
                except:
                    logger.log_debug("ListItemsCommand: '%s' is not a recognized content code" % field)
        except Exception, e:
            logger.log_debug("ListItemsCommand caught exception: %s" % e)
        adbs = CodeBag("adbs")
        adbs.add(ContentCode("mstt", 200))      # status code
        adbs.add(ContentCode("muty", 1))        # always 0?
        songs = Song.objects.all()
        adbs.add(ContentCode("mtco", len(songs)))       # total number of matching records
        adbs.add(ContentCode("mrco", len(songs)))       # total number of records returned
        listing = CodeBag("mlcl")
        for song in songs:
            record = CodeBag("mlit")
            record.add(ContentCode("mikd", 2))                      # item kind (2 for music)
            record.add(ContentCode("miid", int(song.id)))           # item id
            record.add(ContentCode("minm", str(song.name)))         # item name (track name)
            record.add(ContentCode("mper", int(song.id)))           # persistent id
            record.add(ContentCode("asdk", 0))                      # song data kind
            record.add(ContentCode("asul", str('')))                # song data URL
            record.add(ContentCode("asal", str(song.album.name)))
            record.add(ContentCode("agrp", str('')))                # album group?
            record.add(ContentCode("asar", str(song.artist.name)))  # artist name
            record.add(ContentCode("asbr", 0))                      # song bitrate
            record.add(ContentCode("asbt", 0))                      # song beats-per-minute
            record.add(ContentCode("ascm", str('')))                # song comment
            record.add(ContentCode("asco", False))                  # song is compilation?
            record.add(ContentCode("ascp", str('')))                #
            record.add(ContentCode("asda", 1))                      # date added
            record.add(ContentCode("asdm", 1))                      # date modified
            record.add(ContentCode("asdc", 1))                      # disc count
            record.add(ContentCode("asdn", 1))                      # disc number
            record.add(ContentCode("asdb", False))                          # song disabled?
            record.add(ContentCode("aseq", str('')))                        # song EQ preset
            record.add(ContentCode("asfm", "mp3"))                          # file format
            record.add(ContentCode("asgn", str(song.album.genre.name)))     # genre name
            record.add(ContentCode("asdt", str('')))                        # song description
            record.add(ContentCode("asrv", 0))                              # relative volume
            record.add(ContentCode("assr", 0))                              # sample rate
            record.add(ContentCode("assz", int(song.file.size)))            # file size
            record.add(ContentCode("asst", 0))                              # song start time
            record.add(ContentCode("assp", 0))                              # song stop time
            record.add(ContentCode("astm", int(song.duration)))             # song time in ms
            record.add(ContentCode("astc", 1))                              # number of tracks on album
            record.add(ContentCode("astn", int(song.track_number)))         # track number on album
            record.add(ContentCode("asur", 0))                              # song user rating
            record.add(ContentCode("asyr", 0))                              # song publication year
            listing.add(record)
        adbs.add(listing)
        return adbs
        
class StreamSongCommand(Command):
    def __init__(self, songid):
        self.songid = songid
    def render(self, request):
        song = Song.objects.filter(id=self.songid)
        if song == []:
            return Response(404)
        try:
            f = open(song[0].file.path, 'rb')
        except:
            return Response(404) 
        mimetype = song[0].file.mimetype
        logger.log_debug("%s -> %s (%s)" % (request.path, song[0].file.path, mimetype))
        mimetype = MimeType.fromString(mimetype)
        #return Response(200, {'content-type': mimetype}, FileStream(f, useMMap=False))
        return Response(200, {'content-type': x_dmap_tagged}, FileStream(f, useMMap=False))

class ListPlaylistsCommand(Command):
    def __init__(self, dbid):
        self.dbid = dbid
    def locateChild(self, request, segments):
        if len(segments) == 1:
            return self, []
        if not len(segments) == 3:
            return None, []
        try:
            plsid = int(segments[1])
        except:
            return None, []
        return ListPlaylistItemsCommand(plsid), []
    def renderDAAP(self, request):
        aply = CodeBag("aply")
        aply.add(ContentCode("mstt", 200))      # status code
        aply.add(ContentCode("muty", 1))        # always 0?
        aply.add(ContentCode("mtco", 1))        # total number of matching records
        aply.add(ContentCode("mrco", 1))        # total number of records returned
        songs = Song.objects.all()
        listing = CodeBag("mlcl")
        aply.add(listing)
        # base playlist
        item = CodeBag("mlit")
        item.add(ContentCode("miid", 1))
        item.add(ContentCode("mper", 1))
        item.add(ContentCode("minm", str(DaapConfig.SHARE_NAME)))
        item.add(ContentCode("mimc", int(len(songs))))
        item.add(ContentCode("abpl", True))
        listing.add(item)
        # my top rated
        item = CodeBag("mlit")
        item.add(ContentCode("miid", 2))
        item.add(ContentCode("mper", 2))
        item.add(ContentCode("minm", "My Top Rated"))
        item.add(ContentCode("mimc", 0))
        listing.add(item)
        # recently added
        item = CodeBag("mlit")
        item.add(ContentCode("miid", 3))
        item.add(ContentCode("mper", 3))
        item.add(ContentCode("minm", "Recently Added"))
        item.add(ContentCode("mimc", 0))
        listing.add(item)
        # recently played
        item = CodeBag("mlit")
        item.add(ContentCode("miid", 4))
        item.add(ContentCode("mper", 4))
        item.add(ContentCode("minm", "Recently Played"))
        item.add(ContentCode("mimc", 0))
        listing.add(item)
        return aply

class ListPlaylistItemsCommand(Command):
    def __init__(self, plsid):
        self.plsid = plsid
    def renderDAAP(self, request):
        apso = CodeBag("apso")
        apso.add(ContentCode("mstt", 200))      # status code
        apso.add(ContentCode("muty", 1))        # always 0?
        listing = CodeBag("mlcl")
        if self.plsid == 1:
            songs = Song.objects.all()
            apso.add(ContentCode("mtco", len(songs)))   # total number of matching records
            apso.add(ContentCode("mrco", len(songs)))   # total number of records returned
            for song in songs:
                item = CodeBag("mlit")
                item.add(ContentCode("mikd", 2))
                item.add(ContentCode("miid", song.id))
                item.add(ContentCode("mcti", song.id))
                listing.add(item)
        else:
            apso.add(ContentCode("mtco", 0))        # total number of matching records
            apso.add(ContentCode("mrco", 0))        # total number of records returned
        apso.add(listing)
        return apso

class LogoutCommand(Command):
    def render(self, request):
        return Response(200, {'content-type': x_dmap_tagged}, "")

class RootCommand(Resource):
    def locateChild(self, request, segments):
        if segments[0] == "server-info":
            return ServerInfoCommand(), []
        if segments[0] == "content-codes":
            return ContentCodesCommand(), []
        if segments[0] == "login":
            return LoginCommand(), []
        if segments[0] == "update":
            return UpdateCommand(), []
        if segments[0] == "databases":
            return DatabaseCommand(), segments[1:]
        if segments[0] == "logout":
            return LogoutCommand(), []
        return None, []

class DAAPFactory(HTTPFactory):
    def __init__(self):
        HTTPFactory.__init__(self, Site(RootCommand()))
