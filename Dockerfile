FROM	registry.opensuse.org/opensuse/bci/python:latest

RUN	zypper -n install \
		python3-requests \
		python3-requests-toolbelt \
		python3-rpm && \
	zypper clean -a

COPY	susepkg.py /

ENTRYPOINT ["/usr/bin/python3", "/susepkg.py"]
