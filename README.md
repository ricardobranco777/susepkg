# susepkg

Show SUSE package versions

Docker image available at `ghcr.io/ricardobranco777/susepkg:latest`

## Requirements

- Python 3.11+
- python3-requests
- python3-rpm

## Example

```
$ susepkg -a -p SLE-Micro/5.5 podman
4.4.4-150500.1.4
4.7.2-150500.3.3.1
4.8.3-150500.3.6.1
4.8.3-150500.3.9.1
4.9.5-150500.3.12.1
```

## Usage

```
usage: susepkg [-h] [-a] [-A {aarch64,ppc64le,s390x,x86_64}] [--debug] [-i] [-p PRODUCT] [-x] [--version] [package]

show SUSE package versions

positional arguments:
  package

options:
  -h, --help            show this help message and exit
  -a, --all             show all versions
  -A {aarch64,ppc64le,s390x,x86_64}, --arch {aarch64,ppc64le,s390x,x86_64}
  -i, --insensitive     case insensitive search
  -p PRODUCT, --product PRODUCT
                        product or list or any
  -x, --regex           search regular expression
  --version             show program's version number and exit
```

Product list

```
$ susepkg -p list
RES-LTSS/7
RES/7
RES/8
SL-Micro/6.0
SLE-HPC/12.2
SLE-HPC/12.3
SLE-HPC/12.4
SLE-HPC/12.5
SLE-Micro/5.3
SLE-Micro/5.4
SLE-Micro/5.5
SLED/12
SLED/12.1
SLED/12.2
SLED/12.3
SLED/12.4
SLED/15
SLED/15.1
SLED/15.2
SLED/15.3
SLED/15.4
SLED/15.5
SLED/15.6
SLES/12
SLES/12.1
SLES/12.2
SLES/12.3
SLES/12.4
SLES/12.5
SLES/15
SLES/15.1
SLES/15.2
SLES/15.3
SLES/15.4
SLES/15.5
SLES/15.6
SLES_SAP/12
SLES_SAP/12.1
SLES_SAP/12.2
SLES_SAP/12.3
SLES_SAP/12.4
SLES_SAP/12.5
SLES_SAP/15
SLES_SAP/15.1
SLES_SAP/15.2
SLES_SAP/15.3
SLES_SAP/15.4
SLES_SAP/15.5
SLES_SAP/15.6
SLE_HPC/15
SLE_HPC/15.1
SLE_HPC/15.2
SLE_HPC/15.3
SLE_HPC/15.4
SLE_HPC/15.5
SLE_RT/15.1
SLE_RT/15.2
SLE_RT/15.3
SLE_RT/15.4
SLE_RT/15.5
SLL/9
SUSE-Manager-Proxy/4.0
SUSE-Manager-Proxy/4.1
SUSE-Manager-Proxy/4.2
SUSE-Manager-Proxy/4.3
SUSE-Manager-Server/4.0
SUSE-Manager-Server/4.1
SUSE-Manager-Server/4.2
SUSE-Manager-Server/4.3
SUSE-MicroOS/5.0
SUSE-MicroOS/5.1
SUSE-MicroOS/5.2
```

TODO

- Support openSUSE
