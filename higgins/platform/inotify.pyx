# Higgins - A multi-media server
# Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
#
# This program is free software; for license information see
# the COPYING file.

# constants (from sys/inotify.h)
ACCESS          = 0x00000001                            # File was accessed.
MODIFY          = 0x00000002                            # File was modified.
ATTRIB          = 0x00000004                            # Metadata changed.
CLOSE_WRITE     = 0x00000008                            # Writtable file was closed.
CLOSE_NOWRITE   = 0x00000010                            # Unwrittable file closed.
CLOSE           = (CLOSE_WRITE | CLOSE_NOWRITE)         # Close.
OPEN            = 0x00000020                            # File was opened.
MOVED_FROM      = 0x00000040                            # File was moved from X.
MOVED_TO        = 0x00000080                            # File was moved to Y.
MOVE            = (MOVED_FROM | MOVED_TO)               # Moves.
CREATE          = 0x00000100                            # Subfile was created.
DELETE          = 0x00000200                            # Subfile was deleted.
DELETE_SELF     = 0x00000400                            # Self was deleted.
MOVE_SELF       = 0x00000800                            # Self was moved.`

cdef extern from "inotify-internal.h":
    ctypedef struct __inotify_event:
        char *name
        unsigned int wd
        unsigned int cookie
        unsigned int mask
    char *__inotify_strerror()
    int __inotify_open()
    void __inotify_close(int fd)
    int __inotify_add_watch(int fd, char *path, unsigned int flags)
    int __inotify_rm_watch(int fd, int wd)
    int __inotify_start_read(int fd, char *buffer, unsigned int size)
    int __inotify_read_next(char *buffer, int nread, int *curr, __inotify_event *ev)

class InotifyException(Exception):
    def __init__(self, reason):
        self.reason = reason
    def __str__(self):
        return self.reason

def open():
    return __inotify_open ()

def close(fd):
    __inotify_close (fd)

def add_watch(fd, path, flags):
    return __inotify_add_watch (fd, path, flags)

def rm_watch(fd, wd):
    return __inotify_rm_watch (fd, wd)

def get_events(fd):
    cdef char buffer[4096]
    cdef int curr
    cdef int nread
    cdef __inotify_event ev

    events = []
    nread = __inotify_start_read (fd, buffer, 4096)
    if nread < 0:
        raise InotifyException(__inotify_strerror())
    curr = 0
    while True:
        if not __inotify_read_next (buffer, nread, &curr, &ev):
            break
        event = { 'name': ev.name, 'wd': ev.wd, 'cookie': ev.cookie, 'mask': ev.mask }
        events.append(event)
    return events
