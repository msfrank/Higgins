from twisted.internet import defer, reactor
from codebag import CodeBag, ContentCode, render
from content_codes import content_codes, content_code_str_to_int
from higgins.core.models import File, Song
from logger import DAAPLogger
from higgins.conf import conf
import server

class ServerInfoCommand(server.DAAPResource):
    def renderDAAP(self, request):
        msrv = CodeBag("msrv")
        msrv.add(ContentCode("mstt", 200))
        msrv.add(ContentCode("mpro", (2,0,0)))  # version 0.2.0.0
        msrv.add(ContentCode("apro", (3,0,0)))  # version 0.3.0.0
        msrv.add(ContentCode("minm", str(conf.get("DAAP_SHARE_NAME"))))
        msrv.add(ContentCode("mslr", 1))        # login required?
        msrv.add(ContentCode("msau", 0))        # authentication method
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
        return server.DAAPResponse(200, 
                            {'Content-Type': 'application/x-dmap-tagged'},
                            render(msrv))

class ContentCodesCommand(server.DAAPResource):
    def renderDAAP(self, request):
        mccr = CodeBag("mccr")
        mccr.add(ContentCode("mstt", 200))
        for name,value in content_codes.items():
            mdcl = CodeBag("mdcl")
            mdcl.add(ContentCode("mcnm", content_code_str_to_int(name)))
            mdcl.add(ContentCode("mcna", value[1]))
            mdcl.add(ContentCode("mcty", value[0]))
            mccr.add(mdcl)
        return server.DAAPResponse(200, 
                            {'Content-Type': 'application/x-dmap-tagged'},
                            render(mccr))

class LoginCommand(server.DAAPResource):
    def renderDAAP(self, request):
        mlog = CodeBag("mlog")
        mlog.add(ContentCode("mstt", 200))
        mlog.add(ContentCode("mlid", 1000000))
        return server.DAAPResponse(200, 
                            {'Content-Type': 'application/x-dmap-tagged'},
                            render(mlog))

class UpdateCommand(server.DAAPResource, DAAPLogger):
    def _checkForUpdates(self, deferred):
        if self.stop_checking:
            return
        #log_debug("checking for database updates")
        if False:
            deferred.callback(server.DAAPResponse(200,
                                                  {'Content-Type': 'application/x-dmap-tagged'},
                                                  ""))
            return
        reactor.callLater(5, self._checkForUpdates, deferred)

    def _stopChecking(self, unused):
        self.stop_checking = True

    def _renderDAAP_3_7(self, request):
        return self._renderDAAP_3_6(request)

    def _renderDAAP_3_6(self, request):
        try:
            rid = int(request.args.get('revision-number', '0'))
            if rid < 0:
                raise Exception
        except:
            self.log_error("UpdateCommand (3.6): invalid revision-number param")
            return server.DAAPResponse(400)
        try:
            delta = int(request.args.get('delta', '0'))
            if delta < 0:
                raise Exception
        except:
            self.log_error("UpdateCommand (3.6): invalid delta param")
            return server.DAAPResponse(400)
        self.log_debug("UpdateCommand (3.6): revision-number=%i, delta=%i" % (rid,delta))
        if delta == 0:
            mupd = CodeBag("mupd")
            mupd.add(ContentCode("mstt", 200))
            mupd.add(ContentCode("musr", 5))
            return server.DAAPResponse(200, 
                                       {'Content-Type': 'application/x-dmap-tagged'},
                                       render(mupd))
        deferred = defer.Deferred()
        deferred.addBoth(self._stopChecking)
        self.stop_checking = False
        reactor.callLater(5, self._checkForUpdates, deferred)
        return deferred

    def _renderDAAP_3_0(self, request):
        try:
            rid = int(request.args.get('revision-number', '0'))
            if rid < 0:
                raise Exception
        except:
            self.log_error("UpdateCommand (3.0): invalid revision-number param")
            return server.DAAPResponse(400)
        self.log_debug("UpdateCommand (3.0): revision-number=%i" % rid)
        if rid == 0:
            mupd = CodeBag("mupd")
            mupd.add(ContentCode("mstt", 200))
            mupd.add(ContentCode("musr", 5))
            return server.DAAPResponse(200, 
                                       {'Content-Type': 'application/x-dmap-tagged'},
                                       render(mupd))
        deferred = defer.Deferred()
        deferred.addBoth(self._stopChecking)
        self.stop_checking = False
        reactor.callLater(5, self._checkForUpdates, deferred)
        return deferred

    def renderDAAP(self, request):
        if request.daap_client_version == '3.7':
            return self._renderDAAP_3_7(request)
        if request.daap_client_version == '3.6':
            return self._renderDAAP_3_6(request)
        if request.daap_client_version == '3.0':
            return self._renderDAAP_3_0(request)
        self.log_error =("UpdateCommand: failed to render response: unknown version %s" % request.daap_client_version)
        return server.DAAPResponse(400)

class DatabaseCommand(server.DAAPResource):
    def locateResource(self, request, segments):
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
        record.add(ContentCode("miid", 1))                                  # database ID
        record.add(ContentCode("mper", 1))                                  # database persistent ID
        record.add(ContentCode("minm", str(conf.get("DAAP_SHARE_NAME"))))   # db name
        record.add(ContentCode("mimc", len(Song.objects.all())))            # number of db items
        record.add(ContentCode("mctc", 1))                                  # container count
        listing.add(record)
        avdb.add(listing)
        return server.DAAPResponse(200, 
                            {'Content-Type': 'application/x-dmap-tagged'},
                            render(avdb))

class ListItemsCommand(server.DAAPResource, DAAPLogger):
    def __init__(self, dbid):
        self.dbid = dbid
    def locateResource(self, request, segments):
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
                    self.log_debug("ListItemsCommand: '%s' is not a recognized content code" % field)
        except Exception, e:
            self.log_debug("ListItemsCommand caught exception: %s" % e)
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
            record.add(ContentCode("asdb", False))                   # song disabled?
            record.add(ContentCode("aseq", str('')))                # song EQ preset
            record.add(ContentCode("asfm", "mp3"))                  # file format
            record.add(ContentCode("asgn", "Unknown"))              # genre name
            #record.add(ContentCode("asgn", str(song.genre.name)))   # genre name
            record.add(ContentCode("asdt", str('')))                # song description
            record.add(ContentCode("asrv", 0))                      # relative volume
            record.add(ContentCode("assr", 0))                      # sample rate
            record.add(ContentCode("assz", int(song.file.size)))    # file size
            record.add(ContentCode("asst", 0))                      # song start time
            record.add(ContentCode("assp", 0))                      # song stop time
            record.add(ContentCode("astm", int(song.duration)))     # song time in ms
            record.add(ContentCode("astc", 1))                      # number of tracks on album
            record.add(ContentCode("astn", 1))                      # track number on album
            record.add(ContentCode("asur", 0))                      # song user rating
            record.add(ContentCode("asyr", 0))                      # song publication year
            listing.add(record)
        adbs.add(listing)
        return server.DAAPResponse(200, 
                                   {'Content-Type': 'application/x-dmap-tagged'},
                                   render(adbs))
        
class StreamSongCommand(server.DAAPResource, DAAPLogger):
    def __init__(self, songid):
        self.songid = songid
    def renderDAAP(self, request):
        self.log_debug("downloading songid %s" % self.songid)
        song = Song.objects.filter(id=self.songid)
        if song == []:
            return server.DAAPResponse(404)
        try:
            f = open(song[0].file.path, "r")
        except:
            return server.DAAPResponse(404) 
        log_debug("[daap] songid %s -> %s" % (self.songid, song[0].file.path))
        return server.DAAPResponse(200, 
                                   {'Content-Type': song[0].file.mimetype },
                                   server.DAAPFileStream(f))

class ListPlaylistsCommand(server.DAAPResource):
    def __init__(self, dbid):
        self.dbid = dbid
    def locateResource(self, request, segments):
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
        aply.add(ContentCode("mtco", 0))        # total number of matching records
        aply.add(ContentCode("mrco", 0))        # total number of records returned
        listing = CodeBag("mlcl")
        aply.add(listing)
        return server.DAAPResponse(200, 
                            {'Content-Type': 'application/x-dmap-tagged'},
                            render(aply))

class ListPlaylistItemsCommand(server.DAAPResource):
    def __init__(self, plsid):
        self.plsid
    def renderDAAP(self, request):
        apso = CodeBag("apso")
        apso.add(ContentCode("mstt", 200))      # status code
        apso.add(ContentCode("muty", 1))        # always 0?
        apso.add(ContentCode("mtco", 0))        # total number of matching records
        apso.add(ContentCode("mrco", 0))        # total number of records returned
        listing = CodeBag("mlcl")
        apso.add(listing)
        return server.DAAPResponse(200, 
                            {'Content-Type': 'application/x-dmap-tagged'},
                            render(apso))

class LogoutCommand(server.DAAPResource):
    def renderDAAP(self, request):
        return server.DAAPResponse(200, 
                            {'Content-Type': 'application/x-dmap-tagged'},
                            "")

class DAAPCommand(server.DAAPResource):
    def locateResource(self, request, segments):
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
