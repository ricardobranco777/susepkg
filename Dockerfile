FROM	registry.opensuse.org/opensuse/bci/python:3.11

RUN	zypper -n install \
		python3-requests \
		python3-requests-toolbelt \
		python3-rpm && \
	zypper clean -a

COPY	susepkg.py /

ENTRYPOINT ["/usr/bin/python3", "/susepkg.py"]
