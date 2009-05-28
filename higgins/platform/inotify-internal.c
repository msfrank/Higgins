/*
 * Higgins - A multi-media server
 * Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
 *
 * This program is free software; for license information see
 * the COPYING file.
 */

#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <assert.h>
#include <sys/inotify.h>

#include "inotify-internal.h"

static int last_errno = 0;

char *
__inotify_strerror (void)
{
    return strerror (last_errno);
}

int
__inotify_open (void)
{
    return inotify_init ();
}

void
__inotify_close (int fd)
{
    close (fd);
}

int
__inotify_add_watch (int fd, char *path, unsigned int flags)
{
    return inotify_add_watch (fd, path, flags);
}

int
__inotify_rm_watch (int fd, int wd)
{
    return inotify_rm_watch (fd, wd);
}

int
__inotify_start_read (int fd, char *buffer, unsigned int size)
{
    int nread;

    assert (buffer != NULL);
    assert (size > 0);

    memset (buffer, 0, size);
    nread = read (fd, buffer, size);
    if (nread < 0)
        last_errno = errno;
    return nread;
}

int
__inotify_read_next (char *buffer, int nread, int *curr, struct __inotify_event *ev)
{
    struct inotify_event *iev;

    assert (buffer != NULL);
    assert (nread > 0);
    assert (curr != NULL);
    assert (ev != NULL);

    if (*curr >= nread)
        return 0;               /* finished reading events */
    iev = (struct inotify_event *) &buffer[*curr];
    ev->wd = iev->wd;
    ev->mask = iev->mask;
    ev->cookie = iev->cookie;
    ev->name = iev->name;
    *curr += sizeof (struct inotify_event) + iev->len;

    return 1;
}
