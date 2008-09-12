#!/bin/sh
aclocal -I m4
autoconf
automake --copy --add-missing
