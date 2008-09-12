AC_INIT([higgins], 0.0.1, [https://syntaxjockey.com/svn/higgins])
AM_INIT_AUTOMAKE([1.9])
AC_CONFIG_SRCDIR([higgins/__init__.py])
AC_CONFIG_MACRO_DIR([m4])
AM_MAINTAINER_MODE

AM_PATH_PYTHON(2.5)

AM_CHECK_PYMOD([twisted],,, AC_MSG_ERROR([Python module 'twisted' not found]))
AM_CHECK_PYMOD([twisted.web2],,, AC_MSG_ERROR([Python module 'twisted.web2' not found]))
AM_CHECK_PYMOD([sqlite],,, AC_MSG_ERROR([Python module 'sqlite' not found]))
AM_CHECK_PYMOD([django],,, AC_MSG_ERROR([Python module 'django' not found]))
AM_CHECK_PYMOD([dbus],,, AC_MSG_ERROR([Python module 'dbus' not found]))
AM_CHECK_PYMOD([avahi],,, AC_MSG_ERROR([Python module 'avahi' not found]))
AM_CHECK_PYMOD([magic],,, AC_MSG_ERROR([Python module 'magic' not found]))
AM_CHECK_PYMOD([mutagen],,, AC_MSG_ERROR([Python module 'mutagen' not found]))
AM_CHECK_PYMOD([setuptools],,, AC_MSG_ERROR([Python module 'setuptools' not found]))

AC_CONFIG_FILES(
    Makefile
    higgins/Makefile
    higgins/core/Makefile
    data/Makefile
    data/css/Makefile
    data/images/Makefile
    data/templates/Makefile
    scripts/Makefile
    plugins/Makefile
    plugins/upnp/Makefile
    plugins/daap/Makefile)
AC_OUTPUT
