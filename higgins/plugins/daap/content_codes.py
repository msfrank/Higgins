# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

class ContentType:
    Byte = 1
    SignedLong = 2
    Short = 3
    Long = 5
    LongLong = 7
    String = 9
    Date = 10
    Version = 11
    List = 12

def content_code_str_to_int(s):
    from struct import pack, unpack
    temp = pack("4c", s[0],s[1],s[2],s[3])
    i = unpack("l", temp)
    return i[0]

content_codes = {
    'mdcl': (ContentType.List, 'dmap.dictionary'),
    'mstt': (ContentType.Long, 'dmap.status'),
    'miid': (ContentType.Long, 'dmap.itemid'),
    'minm': (ContentType.String, 'dmap.itemname'),
    'mikd': (ContentType.Byte, 'dmap.itemkind'),
    'mper': (ContentType.LongLong, 'dmap.persistentid'),
    'mcon': (ContentType.List, 'dmap.container'),
    'mctc': (ContentType.Long, 'dmap.containercount'),
    'mcti': (ContentType.Long, 'dmap.containeritemid'),
    'mpco': (ContentType.Long, 'dmap.parentcontainerid'),
    'msts': (ContentType.String, 'dmap.statusstring'),
    'mimc': (ContentType.Long, 'dmap.itemcount'),
    'mrco': (ContentType.Long, 'dmap.returnedcount'),
    'mtco': (ContentType.Long, 'dmap.specifiedtotalcount'),
    'mlcl': (ContentType.List, 'dmap.listing'),
    'mlit': (ContentType.List, 'dmap.listingitem'),
    'mbcl': (ContentType.List, 'dmap.bag'),
    'mdcl': (ContentType.List, 'dmap.dictionary'),
    'msrv': (ContentType.List, 'dmap.serverinforesponse'),
    'msau': (ContentType.Byte, 'dmap.authenticationmethod'),
    'mslr': (ContentType.Byte, 'dmap.loginrequired'),
    'mpro': (ContentType.Version, 'dmap.protocolversion'),
    'apro': (ContentType.Version, 'daap.protocolversion'),
    'msal': (ContentType.Byte, 'dmap.supportsuatologout'),
    'msup': (ContentType.Byte, 'dmap.supportsupdate'),
    'mspi': (ContentType.Byte, 'dmap.supportspersistentids'),
    'msex': (ContentType.Byte, 'dmap.supportsextensions'),
    'msbr': (ContentType.Byte, 'dmap.supportsbrowse'),
    'msqy': (ContentType.Byte, 'dmap.supportsquery'),
    'msix': (ContentType.Byte, 'dmap.supportsindex'),
    'msrs': (ContentType.Byte, 'dmap.supportsresolve'),
    'mstm': (ContentType.Long, 'dmap.timeoutinterval'),
    'msdc': (ContentType.Long, 'dmap.databasescount'),
    'mccr': (ContentType.List, 'dmap.contentcodesresponse'),
    'mcnm': (ContentType.Long, 'dmap.contentcodesnumber'),
    'mcna': (ContentType.String, 'dmap.contentcodesname'),
    'mcty': (ContentType.Short, 'dmap.contentcodestype'),
    'mlog': (ContentType.List, 'dmap.loginresponse'),
    'mlid': (ContentType.Long, 'dmap.sessionid'),
    'mupd': (ContentType.List, 'dmap.updateresponse'),
    'musr': (ContentType.Long, 'dmap.serverrevision'),
    'muty': (ContentType.Byte, 'dmap.updatetype'),
    'mudl': (ContentType.List, 'dmap.deletedidlisting'),
    'avdb': (ContentType.List, 'daap.serverdatabases'),
    'abro': (ContentType.List, 'daap.databasebrowse'),
    'abal': (ContentType.List, 'daap.browsealbumlistung'),
    'abar': (ContentType.List, 'daap.browseartistlisting'),
    'abcp': (ContentType.List, 'daap.browsecomposerlisting'),
    'abgn': (ContentType.List, 'daap.browsegenrelisting'),
    'adbs': (ContentType.List, 'daap.databasesongs'),
    'agrp': (ContentType.String, 'daap.songgrouping'),
    'asal': (ContentType.String, 'daap.songalbum'),
    'asar': (ContentType.String, 'daap.songartist'),
    'asbt': (ContentType.Short, 'daap.songbeatsperminute'),
    'asbr': (ContentType.Short, 'daap.songbitrate'),
    'ascm': (ContentType.String, 'daap.songcomment'),
    'asco': (ContentType.Byte, 'daap.songcompilation'),
    'ascp': (ContentType.String, 'daap.songcomposer'),
    'asda': (ContentType.Date, 'daap.songdateadded'),
    'asdm': (ContentType.Date, 'daap.songdatemodified'),
    'asdc': (ContentType.Short, 'daap.songdisccount'),
    'asdn': (ContentType.Short, 'daap.songdiscnumber'),
    'asdb': (ContentType.Byte, 'daap.songdisabled'),
    'aseq': (ContentType.String, 'daap.songeqpreset'),
    'asfm': (ContentType.String, 'daap.songformat'),
    'asgn': (ContentType.String, 'daap.songgenre'),
    'asdt': (ContentType.String, 'daap.songdescription'),
    'asrv': (ContentType.Byte, 'daap.songrelativevolume'),
    'assr': (ContentType.Long, 'daap.songsamplerate'),
    'assz': (ContentType.Long, 'daap.songsize'),
    'asst': (ContentType.Long, 'daap.songstarttime'),
    'assp': (ContentType.Long, 'daap.songstoptime'),
    'astm': (ContentType.Long, 'daap.songtime'),
    'astc': (ContentType.Short, 'daap.songtrackcount'),
    'astn': (ContentType.Short, 'daap.songtracknumber'),
    'asur': (ContentType.Byte, 'daap.songuserrating'),
    'asyr': (ContentType.Short, 'daap.songyear'),
    'asdk': (ContentType.Byte, 'daap.songdatakind'),
    'asul': (ContentType.String, 'daap.songdataurl'),
    'ascd': (ContentType.Long, 'daap.songcodectype'),
    'ascs': (ContentType.Long, 'daap.songcodecsubtype'),
    'aply': (ContentType.List, 'daap.databaseplaylists'),
    'abpl': (ContentType.Byte, 'daap.baseplaylist'),
    'apso': (ContentType.List, 'daap.playlistsongs'),
    'prsv': (ContentType.List, 'daap.resolve'),
    'arif': (ContentType.List, 'daap.resolveinfo'),
    'aeNV': (ContentType.Long, 'com.apple.itunes.norm-volume'),
    'aeSP': (ContentType.Byte, 'com.apple.itunes.smart-playlist'),
}

reverse_table = {}
for code,(type,cname) in content_codes.items():
    reverse_table[cname] = code
