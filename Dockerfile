FROM	registry.opensuse.org/opensuse/bci/python:3.11

RUN	zypper -n install \
		python3-attrs \
		python3-cattrs \
		python3-requests \
		python3-requests-cache \
		python3-requests-toolbelt \
		python3-rpm && \
	zypper clean -a

COPY	susepkg /susepkg

VOLUME	/root

ENTRYPOINT ["/usr/bin/python3", "/susepkg"]
