# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

import random
from twisted.internet import defer, reactor
from higgins.http.channel import HTTPFactory
from higgins.http.server import Site
from higgins.http.http import Response
from higgins.http.resource import Resource
from higgins.http.stream import SimpleStream, FileStream
from higgins.http.http_headers import MimeType
from higgins.db import db, File, Song, Playlist
from higgins.plugins.daap import DaapConfig, DaapPrivate
from higgins.plugins.daap.codebag import CodeBag, ContentCode
from higgins.plugins.daap.content_codes import content_codes, content_code_str_to_int
from higgins.plugins.daap.logger import logger

x_dmap_tagged = MimeType('application', 'x-dmap-tagged')

class Command(Resource):
    """The base class for a DAAP command."""
    def __init__(self, service):
        self.service = service

    def renderDAAP(self, request):
        """
        This method is invoked for GET requests on this resource.  Subclasses
        should return a CodeBag which is rendered as the response body, or raise
        an Exception if an error occurred.
        """
        raise Exception('Not Implemented')

    def allowedMethods(self):
        """The only allowed method is a GET request."""
        return ('GET',)

    def render(self, request):
        """calls the renderDAAP method and returns its result."""
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
        msrv.add(ContentCode("mslr", 0))        # login required?
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
        # generate an unused session id
        sid = 0
        while sid == 0:
            sid = random.randint(1,2**31 - 1)
            if sid in self.service.sessions:
                sid = 0
            else:
                self.service.sessions[sid] = sid
        # return the login response
        mlog = CodeBag("mlog")
        mlog.add(ContentCode("mstt", 200))
        mlog.add(ContentCode("mlid", sid))
        return mlog

class UpdateStream(SimpleStream):
    def __init__(self, service):
        self._DBChanged = False
        self.length = 32
        self._signal = db.db_changed.connect()
        self._signal.addCallback(self._setDBChanged)
        self.deferred = defer.Deferred()
        self.deferred.addCallback(self._render)
        reactor.callLater(2, self._checkForUpdate)
        self._service = service
        self._service.streams[self] = self
    def _setDBChanged(self, unused):
        self._DBChanged = True
        self._signal = None
    def _checkForUpdate(self):
        if not self.deferred:
            return
        if not self._DBChanged:
            reactor.callLater(2, self._checkForUpdate)
            return
        new_revision = DaapPrivate.REVISION_NUMBER + 1
        DaapPrivate.REVISION_NUMBER = new_revision
        self.deferred.callback(new_revision)
    def _render(self, revision):
        if revision > 0:
            logger.log_debug("UpdateStream: new revision is %i" % revision)
        else:
            logger.log_debug("UpdateStream: signaling disconnect (revision %i)" % revision)
        # if _caughtUpdate was not called, then disconnect from the signal
        if self._signal:
            db.db_changed.disconnect(self._signal)
            self._signal = None
        # delete the reference to self.deferred
        self.deferred = None
        self.length = 0
        # remove stream from service.streams
        del self._service.streams[self]
        # write response
        mupd = CodeBag("mupd")
        mupd.add(ContentCode("mstt", 200))
        mupd.add(ContentCode("musr", int(revision)))
        return str(mupd.render())
    def read(self):
        if self.deferred:
            logger.log_debug("UpdateStream: waiting for new revision")
            return self.deferred
        logger.log_debug("UpdateStream: finished read")
        return None
    def close(self):
        self.deferred = None
        self.length = 0
        logger.log_debug("UpdateStream: closed stream")

class UpdateCommand(Command):
    def render(self, request):
        logger.log_debug("%s %s" % (request.method, request.path))
        logger.log_debug(str(request.args))
        try:
            # get session id
            sid = request.args.get('session-id', ['0'])
            sid = int(sid[0])
            if sid == 0 or not sid in self.service.sessions:
                raise Exception("session-id %i is invalid" % sid)
            # get revision number
            rid = request.args.get('revision-number', ['0'])
            rid = int(rid[0])
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
            # create a new update stream to listen for db-changed signal
            stream = UpdateStream(self.service)
            return Response(200, { 'content-type': x_dmap_tagged }, stream)
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
        record.add(ContentCode("mimc", db.count(Song)))                 # number of db items
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
    def _retrieveSongs(self, d, adbs, listing, songs):
        try:
            logger.log_debug("ListItemsCommand: retrieving 20 song items")
            # retrieve up to 20 songs
            i = 0
            while i < 20:
                song = songs.next()
                logger.log_debug("ListItemsCommand: got item %s" % song)
                item = CodeBag("mlit")
                item.add(ContentCode("mikd", 2))                              # item kind (2 for music)
                item.add(ContentCode("miid", int(song.storeID)))              # item id
                item.add(ContentCode("minm", str(song.name)))                 # item name (track name)
                item.add(ContentCode("mper", int(song.storeID)))              # persistent id
                item.add(ContentCode("asdk", 0))                              # song data kind
                item.add(ContentCode("asul", str('')))                        # song data URL
                item.add(ContentCode("asal", str(song.album.name)))
                item.add(ContentCode("agrp", str('')))                        # album group?
                item.add(ContentCode("asar", str(song.artist.name)))          # artist name
                item.add(ContentCode("asbr", 0))                              # song bitrate
                item.add(ContentCode("asbt", 0))                              # song beats-per-minute
                item.add(ContentCode("ascm", str('')))                        # song comment
                item.add(ContentCode("asco", False))                          # song is compilation?
                item.add(ContentCode("ascp", str('')))                        #
                item.add(ContentCode("asda", 1))                              # date added
                item.add(ContentCode("asdm", 1))                              # date modified
                item.add(ContentCode("asdc", 1))                              # disc count
                item.add(ContentCode("asdn", 1))                              # disc number
                item.add(ContentCode("asdb", False))                          # song disabled?
                item.add(ContentCode("aseq", str('')))                        # song EQ preset
                item.add(ContentCode("asfm", "mp3"))                          # file format
                item.add(ContentCode("asgn", str(song.album.genre.name)))     # genre name
                item.add(ContentCode("asdt", str('')))                        # song description
                item.add(ContentCode("asrv", 0))                              # relative volume
                item.add(ContentCode("assr", 0))                              # sample rate
                item.add(ContentCode("assz", int(song.file.size)))            # file size
                item.add(ContentCode("asst", 0))                              # song start time
                item.add(ContentCode("assp", 0))                              # song stop time
                item.add(ContentCode("astm", int(song.duration)))             # song time in ms
                item.add(ContentCode("astc", 1))                              # number of tracks on album
                item.add(ContentCode("astn", int(song.trackNumber)))          # track number on album
                item.add(ContentCode("asur", 0))                              # song user rating
                item.add(ContentCode("asyr", 0))                              # song publication year
                listing.add(item)
                i += 1
            # pass control back to twisted for a while
            reactor.callLater(0, self._retrieveSongs, d, adbs, listing, songs)
        except StopIteration:
            pass
        except Exception, e:
            d.errback(e)
        d.callback(adbs)

    def _renderDAAP(self, adbs):
        return Response(200, { 'content-type': x_dmap_tagged }, adbs.render())

    def _errDAAP(self, failure):
        logger.log_error("ListItemsCommand failed: %s" % failure)
        return Response(400, { 'content-type': MimeType('text','plain') }, str(failure))

    def render(self, request):
        logger.log_debug("%s %s" % (request.method, request.path))
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
        songs = db.query(Song)
        songcount = songs.count()
        adbs.add(ContentCode("mtco", songcount))       # total number of matching records
        adbs.add(ContentCode("mrco", songcount))       # total number of records returned
        listing = CodeBag("mlcl")
        adbs.add(listing)
        d = defer.Deferred()
        d.addCallback(self._renderDAAP)
        d.addErrback(self._errDAAP)
        reactor.callLater(0, self._retrieveSongs, d, adbs, listing, songs.paginate())
        return d

class StreamSongCommand(Command):
    def __init__(self, songid):
        self.songid = songid
    def render(self, request):
        song = db.get(Song, Song.storeID==int(self.songid))
        if song == None:
            return Response(404)
        try:
            f = open(song.file.path, 'rb')
        except EnvironmentError, (errno, reason):
            logger.log_debug("failed to open song %s: %s" % (song.file.path, reason))
            return Response(404) 
        mimetype = str(song.file.MIMEType)
        logger.log_debug("%s -> %s (%s)" % (request.path, song.file.path, mimetype))
        #mimetype = MimeType.fromString(mimetype)
        return Response(200, {'content-type': x_dmap_tagged}, FileStream(f))

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
        songs = db.query(Song)
        listing = CodeBag("mlcl")
        aply.add(listing)
        # base playlist
        item = CodeBag("mlit")
        item.add(ContentCode("miid", 1))    
        item.add(ContentCode("mper", 1))
        item.add(ContentCode("minm", str(DaapConfig.SHARE_NAME)))
        item.add(ContentCode("mimc", int(songs.count())))
        item.add(ContentCode("abpl", 1))
        listing.add(item)
        # add each playlist
        for pls in db.query(Playlist):
            item = CodeBag("mlit")
            item.add(ContentCode("miid", pls.storeID + 1))
            item.add(ContentCode("mper", pls.storeID + 1))
            item.add(ContentCode("minm", str(pls.name)))
            item.add(ContentCode("mimc", pls.length))
            listing.add(item)
        return aply

class ListPlaylistItemsCommand(Command):
    def __init__(self, plsid):
        self.plsid = int(plsid) - 1
    def _retrieveSongs(self, d, apso, listing, songs):
        try:
            # retrieve up to 20 songs
            i = 0
            while i < 20:
                song = songs.next()
                item = CodeBag("mlit")
                item.add(ContentCode("mikd", 2))
                item.add(ContentCode("miid", song.storeID))
                item.add(ContentCode("mcti", song.storeID))
                listing.add(item)
                i += 1
            # pass control back to twisted for a while
            reactor.callLater(0, self._retrieveSongs, d, apso, listing, songs)
        except StopIteration:
            pass
        except Exception, e:
            d.errback(e)
        d.callback(apso)
    def _renderDAAP(self, apso):
        return Response(200, { 'content-type': x_dmap_tagged }, apso.render())
    def _errDAAP(self, failure):
        logger.log_error("ListItemsCommand failed: %s" % failure)
        return Response(400, { 'content-type': MimeType('text','plain') }, str(failure))
    def render(self, request):
        logger.log_debug("%s %s" % (request.method, request.path))
        logger.log_debug(str(request.args))
        apso = CodeBag("apso")
        apso.add(ContentCode("mstt", 200))      # status code
        apso.add(ContentCode("muty", 1))        # always 1?
        # a playlist id of 0 is special and means list all items in the database.
        if self.plsid == 0:
            q = db.query(Song)
            songs = q.paginate()
            numSongs = q.count()
        # otherwise look up the playlist with the specified id
        else:
            q = db.get(Playlist, Playlist.storeID==int(self.plsid))
            songs = q.listSongs()
            numSongs = q.length
        apso.add(ContentCode("mtco", numSongs))   # total number of matching records
        apso.add(ContentCode("mrco", numSongs))   # total number of records returned
        listing = CodeBag("mlcl")
        apso.add(listing)
        d = defer.Deferred()
        d.addCallback(self._renderDAAP)
        d.addErrback(self._errDAAP)
        reactor.callLater(0, self._retrieveSongs, d, apso, listing, songs)
        return d

class LogoutCommand(Command):
    def render(self, request):
        return Response(200, {'content-type': x_dmap_tagged}, "")

class RootCommand(Resource):
    def __init__(self, service):
        self.service = service
        Resource.__init__(self)
    def locateChild(self, request, segments):
        if segments[0] == "server-info":
            return ServerInfoCommand(self.service), []
        if segments[0] == "content-codes":
            return ContentCodesCommand(self.service), []
        if segments[0] == "login":
            return LoginCommand(self.service), []
        if segments[0] == "update":
            return UpdateCommand(self.service), []
        if segments[0] == "databases":
            return DatabaseCommand(self.service), segments[1:]
        if segments[0] == "logout":
            return LogoutCommand(self.service), []
        return None, []

class DAAPFactory(HTTPFactory):
    def __init__(self, service):
        self.service = service
        HTTPFactory.__init__(self, Site(RootCommand(service)))
