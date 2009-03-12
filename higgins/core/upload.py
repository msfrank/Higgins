# Portions of this script (the multipart form uploading) come from:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146306

from sys import argv, exit
from os import stat, walk
from os.path import abspath, basename, join as pathjoin
import httplib, urllib
from mutagen import File
from twisted.python import usage, log
from higgins.logger import Loggable, LEVELS

class UploaderException(Exception):
    def __init__(self, reason):
        self.reason = reason
    def __str__(self):
        return self.reason

class Uploader(object, Loggable):
    domain = 'uploader'
    boundary = '----------ThIs_Is_tHe_bouNdaRY_$'

    def __init__(self, paths, host='localhost', port=8000, isLocal=False, recursive=False):
        self.paths = paths
        self.host = host
        self.log_debug("host: %s" % host)
        self.port = port
        self.log_debug("port: %i" % port)
        self.isLocal = isLocal
        self.log_debug("local-mode: %s" % str(isLocal))
        self.recursive = recursive
        self.log_debug("recursive: %s" % str(recursive))

    def _get_metadata(self, path):
        metadata = {}
        try:
            f = File(path)
            metadata['mimetype'] = f.mime[0]
            metadata['artist'] = u''.join(f['TPE1'].text)
            metadata['album'] = u''.join(f['TALB'].text)
            metadata['title'] = u''.join(f['TIT2'].text)
            metadata['genre'] = u''.join(f['TCON'].text)
            metadata['length'] = str(int(f.info.length*1000))
            metadata['bitrate'] = str(f.info.bitrate)
            metadata['samplerate'] = str(f.info.sample_rate)
            # hack to deal with TRCK tags formatted as numerator/denominator
            try:
                track_num = int(f['TRCK'])
                metadata['track'] = u''.join(f['TRCK'].text)
            except:
                a = str(f['TRCK']).split('/')
                metadata['track'] = str(a[0])
            return metadata
        except KeyError, e:
            raise UploaderException("missing metadata field %s" % e)
        except Exception, e:
            raise e

    def _upload(self, file, metadata):
        # create the multipart body
        lines = []
        # add each metadata part
        for (key, value) in metadata.items():
            lines.append('--' + self.boundary)
            lines.append('Content-Disposition: form-data; name="%s"' % key)
            lines.append('')
            lines.append(value)
        if self.isLocal:
            post_uri = '/manage/create/?is_local=True'
            file_size = 0
        else:
            # if not local mode, then add the headers for the file part
            lines.append('--' + self.boundary)
            lines.append('Content-Disposition: form-data; name="file"; filename="%s"' % basename(file))
            lines.append('Content-Type: %s' % metadata['mimetype'])
            lines.append('')
            lines.append('')
            post_uri = '/manage/create/'
            st = stat(file)
            file_size = st.st_size
        output = '\r\n'.join(lines)
        # create the http client connection
        request = httplib.HTTPConnection("%s:%i" % (self.host,self.port))
        request.putrequest('POST', post_uri)
        request.putheader('User-Agent', 'higgins-uploader')
        request.putheader('Content-Type', 'multipart/form-data; boundary=%s' % self.boundary)
        request.putheader('Content-Length', len(output) + file_size)
        request.endheaders()
        request.send(output)
        nread = len(output)
        if not self.isLocal:
            # if not local mode, then write the file
            f = open(file, 'rb')
            output = f.read(4096)
            request.send(output)
            nread += len(output)
            while not output == "":
                output = f.read(4096)
                request.send(output)
                nread += len(output)
            f.close()
        self.log_debug("wrote %i bytes" % nread)
        response = request.getresponse()
        self.log_debug("server returned status code %s: %s" % (response.status,response.read()))
        return response.status  
        
    def _process_file(self, path):
        try:
            metadata = self._get_metadata(path)
            if self.isLocal:
                metadata['local_path'] = path
            self.log_debug("parsed metadata: %s" % metadata)
            result = self._upload(path, metadata)
            self.log_info("uploaded %s" % path)
        except Exception, e:
            self.log_warning("skipped %s: %s" % (path, e))
 
    def run(self):
        if self.recursive:
            for dir in self.paths:
                for root,dirs,files in walk(dir, topdown=True):
                    self.log_info("processing directory %s" % root)
                    for file in files:
                        file = abspath(pathjoin(root,file))
                        self._process_file(file)
        else:
            for file in self.paths:
                file = abspath(file)
                self._process_file(file)
 
class UploaderObserver(log.DefaultObserver):
    def __init__(self, verbosity=0):
        self.verbosity = verbosity
    def _emit(self, params):
        level = params['level']
        if level <= self.verbosity:
            print ''.join(params['message'])

class UploaderOptions(usage.Options):
    optFlags = [
        ['local-mode', 'l', None],
        ['recursive', 'r', None],
    ]
    optParameters = [
        ['host', 'h', 'localhost', None],
        ['port', 'p', 8000, None, int],
    ]

    def __init__(self):
        usage.Options.__init__(self)
        self['verbose'] = 2

    def opt_quiet(self):
        if self['verbose'] > 0: 
            self['verbose'] = self['verbose'] - 1
    opt_q = opt_quiet

    def opt_verbose(self):
        if self['verbose'] < 5: 
            self['verbose'] = self['verbose'] + 1
    opt_v = opt_verbose

    def parseArgs(self, *paths):
        if len(paths) == 0:
            raise UploaderException("No media files specified.")
        self['paths'] = paths

    def opt_help(self):
        import sys
        print "Usage: %s [OPTIONS...] FILE..." % basename(argv[0])
        print "       %s [OPTIONS...] -r DIR..." % basename(argv[0])
        print ""
        print "  --local-mode,-l        File itself will not be uploaded"
        print "  --host,-h HOST         The host to upload to.  Default is 'localhost'"
        print "  --port,-p PORT         The port higgins is running on.  Default is '8000'"
        print "  --recursive,-r         Recursively upload media files in directories"
        print "  --help                 Display this help"
        print "  --version              Display the version"
        print ""
        exit(0)

    def opt_version(self):
        from higgins import VERSION
        print "Higgins uploader version " + VERSION
        exit(0)

def run_application():
    try:
        o = UploaderOptions()
        o.parseOptions(argv[1:])
        observer = UploaderObserver(verbosity=o['verbose'])
        observer.start()
        uploader = Uploader(o['paths'], host=o['host'], port=o['port'],
            isLocal=o['local-mode'], recursive=o['recursive'])
        uploader.run()
        observer.stop()
        exit(0)
    except usage.UsageError, e:
        print "Error parsing options: %s" % e
        print ""
        print "Try %s --help for usage information." % basename(argv[0])
    except UploaderException, e:
        print "%s" % e
    exit(1)
