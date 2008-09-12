higginsbindir = $(bindir)
higginsbin_SCRIPTS = higgins-media-server higgins-upload

higgins-media-server: higgins-media-server.in
	sed \
		-e 's|@pythondir[@]|$(pythondir)|g' \
		$< > $@.tmp
	chmod 0755 $@.tmp
	mv $@.tmp $@

BUILT_SOURCES = higgins-media-server
CLEANFILES = $(BUILT_SOURCES)
DISTCLEANFILES = $(CLEANFILES)

EXTRA_DIST = higgins-media-server.in higgins-upload
