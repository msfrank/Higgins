# Portions of this script (the multipart form uploading) come from:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146306

from sys import argv, exit
from getopt import gnu_getopt
import httplib, urllib
from os import stat
from os.path import abspath,basename
from mutagen import File

class Uploader(object):

    boundary = '----------ThIs_Is_tHe_bouNdaRY_$'

    def __init__(self, files, host='localhost', port=8000, isLocal=True):
        self.files = files
        self.host = host
        self.port = port
        self.isLocal = isLocal

    def _log(self):
        pass

    def _get_metadata(path):
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
            raise Exception("missing metadata field %s" % e)
        except Exception, e:
            raise e

    def _upload(self, file, metadata):
        # create the multipart body
        lines = []
        # add each metadata part
        for (key, value) in metadata.items():
            print "form-data: '%s' => '%s' (%i bytes)" % (key,value,len(value))
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
        request = httplib.HTTPConnection(host)
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
        print "wrote %i bytes" % nread
        response = request.getresponse()
        print "Server returned status %s: %s" % (response.status,response.read())
        return response.status  
        
    def run(self):
        for path in args:
            try:
                path = abspath(path)
                metadata = get_metadata(path)
                if local_mode:
                    metadata['local_path'] = path
                for datum in metadata.items():
                    print "    %s: %s" % datum
                print "----------------------------------------"
                print "Uploading file to media server at %s ..." % host
                if local_mode:
                    result = do_local_upload(host, path, metadata)
                else:
                    result = do_upload(host, path, metadata)
            except Exception, e:
                print "Failed to process %s: %s" % (path, e)
 
def run_application():

    from twisted.python import usage
    class HigginsOptions(usage.Options):
        optFlags = [
            ["create", "c", "Create the environment if necessary"],
            ["debug", "d", "Run Higgins in the foreground, and log everything to stdout"],
        ]

        def __init__(self):
            usage.Options.__init__(self)
            self['verbose'] = 0

        def opt_verbose(self):
            if self['verbose'] < 3: 
                self['verbose'] = self['verbose'] + 1
        opt_v = opt_verbose

        def parseArgs(self, *files):
            self['files'] = files

        def postOptions(self):
            pass

        def opt_help(self):
            import sys
            print "Usage: %s [-h HOST] [-l] FILE..." % sys.argv[0]
            print ""
            print "  -h HOST       The host to upload to.  Default is 'localhost:8000'"
            print "  -l            Enables local mode (File itself will not be uploaded)"
            print ""
            sys.exit(0)

        def opt_version(self):
            print "Higgins uploader version 0.1"
            sys.exit(0)
    try:
        o = HigginsOptions(self)
        o.parseOptions(options)
        uploader = Uploader(o.files)
        uploader.run()
        exit(0)
    except usage.UsageError, e:
        print "Error parsing options: %s" % e
        print ""
        print "Try --help for usage information.")
    except Exception, e:
        print "%s" % e
    sys.exit(1)
