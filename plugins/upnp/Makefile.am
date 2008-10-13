EXTRA_DIST = \
	setup.py \
	higgins_upnp/__init__.py \
	higgins_upnp/connection_manager.py \
	higgins_upnp/content_directory.py \
	higgins_upnp/media_server.py \
	higgins_upnp/soap_resource.py \
	higgins_upnp/ssdp_server.py \
	higgins_upnp/netif-internal.c \
	higgins_upnp/netif-internal.h \
	higgins_upnp/netif.pyx

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
