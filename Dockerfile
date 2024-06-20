FROM	registry.opensuse.org/opensuse/bci/python:3.11

RUN	zypper -n install \
		python3-packaging \
		python3-requests

COPY	susepkg /susepkg

ENTRYPOINT ["/usr/bin/python3", "/susepkg"]
