/*
 * Higgins - A multi-media server
 * Copyright (c) 2007-2009  Michael Frank <msfrank@syntaxjockey.com>
 *
 * This program is free software; for license information see
 * the COPYING file.
 */

#ifndef INOTIFY_INTERNAL_H
#define INOTIFY_INTERNAL_H

struct __inotify_event {
    char *name;
    unsigned int wd;
    unsigned int cookie;
    unsigned int mask;
};
typedef struct __inotify_event __inotify_event;

char *__inotify_strerror (void);
int __inotify_open (void);
void __inotify_close (int fd);
int __inotify_add_watch (int fd, char *path, unsigned int flags);
int __inotify_rm_watch (int fd, int wd);
int __inotify_start_read (int fd, char *buffer, unsigned int size);
int __inotify_read_next (char *buffer, int nread, int *curr, struct __inotify_event *ev);

#endif
