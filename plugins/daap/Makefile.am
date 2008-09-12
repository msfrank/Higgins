EXTRA_DIST = \
	setup.py \
	higgins_daap/codebag.py \
	higgins_daap/commands.py \
	higgins_daap/content_codes.py \
	higgins_daap/server.py \
	higgins_daap/__init__.py

build.stamp: $(EXTRA_DIST)
	touch build.stamp
	$(PYTHON) setup.py bdist_egg

all: build.stamp

install-data-am: build.stamp
	for egg in `ls -1 dist/*.egg`; do \
		$(install_sh) $$egg $(localstatedir)/higgins/plugins; \
	done

clean:
	rm -rf build.stamp build dist *.egg-info
