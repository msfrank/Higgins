SUBDIRS = core

higginsdir = $(pythondir)/higgins
higgins_PYTHON = __init__.py loader.py logging.py conf.py
nodist_higgins_PYTHON = site_settings.py

site_settings.py: site_settings.py.in
	sed \
		-e 's|@sysconfdir[@]|$(sysconfdir)|g' \
		-e 's|@localstatedir[@]|$(localstatedir)|g' \
		-e 's|@datadir[@]|$(datadir)|g' \
		$< > $@.tmp
	mv $@.tmp $@

install-data-hook:
	mkdir -p $(localstatedir)/higgins
	mkdir -p $(localstatedir)/higgins/plugins

clean-local:
	rm -f *.pyc *.pyo

BUILT_SOURCES = site_settings.py
CLEANFILES = $(BUILT_SOURCES)
DISTCLEANFILES = $(CLEANFILES)

EXTRA_DIST = site_settings.py.in
