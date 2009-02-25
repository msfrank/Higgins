#!/usr/bin/env python

#
# Portions of this script (the multipart form uploading) come from:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146306
#

from sys import argv, exit
from getopt import gnu_getopt
import httplib, urllib
from os import stat
from os.path import abspath,basename
from mutagen import File

class Uploader(object):

    boundary = '----------ThIs_Is_tHe_bouNdaRY_$'

    def __init__(self, files):

    def log(self):

    def do_upload(host, file, metadata):
        st = stat(file)
        lines = []
        for (key, value) in metadata.items():
            lines.append('--' + boundary)
            lines.append('Content-Disposition: form-data; name="%s"' % key)
            lines.append('')
            lines.append(value)
        lines.append('--' + boundary)
        lines.append('Content-Disposition: form-data; name="file"; filename="%s"' % basename(file))
        lines.append('Content-Type: %s' % metadata['mimetype'])
        lines.append('')
        lines.append('')
        output = '\r\n'.join(lines)

        request = httplib.HTTPConnection(host)
        request.putrequest('POST', "/manage/create/")
        request.putheader('User-Agent', 'higgins-uploader')
        request.putheader('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
        request.putheader('Content-Length', len(output) + st.st_size)
        request.endheaders()
        request.send(output)

        nread = len(output)
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

#
#
#
def do_local_upload(host, file, metadata):
    lines = []
    print "sending preamble.."
    for (key, value) in metadata.items():
        lines.append('--' + boundary)
        lines.append('Content-Disposition: form-data; name="%s"' % key)
        lines.append('')
        lines.append(value)
        print "form-data: '%s' => '%s' (%i bytes)" % (key,value,len(value))
    output = '\r\n'.join(lines)

    request = httplib.HTTPConnection(host)
    selector = "/manage/create/?is_local=true"
    request.putrequest('POST', selector)
    request.putheader('Content-Length', len(output))
    request.putheader('User-Agent', 'higgins-uploader')
    request.putheader('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
    request.endheaders()
    request.send(output)
    response = request.getresponse()
    print "Server returned status %s: %s" % (response.status,response.read())
    return response.status  

#
#
#
def get_metadata(path):
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

def print_help():
    print "Usage: higgins-upload [-h HOST] [-l] FILE..."
    print ""
    print "  -h HOST       The host to upload to.  Default is 'localhost:8000'"
    print "  -l            Enables local mode (File itself will not be uploaded)"
    print ""

if __name__ == '__main__':
    host = 'localhost:8000'

    if len(argv) == 1:
        print_help()
        exit(1)
    opts,args = gnu_getopt(argv[1:], 'h:l')
    if len(args) == 0:
        print_help()
        exit(1)
    local_mode = False
    verbosity = 0
    for opt,arg in opts:
        if opt == '-h':
            host = arg
        if opt == '-l':
            local_mode = True
        
    print "========================================"
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
        finally:
            print "========================================"
    exit(0)
