![Build Status](https://github.com/ricardobranco777/susepkg/actions/workflows/ci.yml/badge.svg)

# susepkg

Show SUSE package versions using [documented API](https://scc.suse.com/api/package_search/v4/documentation)

Docker image available at `ghcr.io/ricardobranco777/susepkg:latest`

## Requirements

podman or docker for Docker image, otherwise:

- Python 3.11+
- python3-requests
- python3-rpm

## Usage

```
usage: susepkg [-h] [-a {aarch64,ppc64le,s390x,x86_64}] [-i] -p PRODUCT [-x] [--version] [package]

show SUSE package versions

positional arguments:
  package               may be a shell pattern or regular expression

options:
  -h, --help            show this help message and exit
  -a {aarch64,ppc64le,s390x,x86_64}, --arch {aarch64,ppc64le,s390x,x86_64}
  -i, --insensitive     case insensitive search
  -p PRODUCT, --product PRODUCT
                        product or 'list' or 'any'. May be specified multiple times
  -x, --regex           search regular expression
  --version             show program's version number and exit
```

## Example usage

- `susepkg -p any podman`
- `susepkg -p SL-Micro/6.0 \*podman\*`
- `susepkg -p SL-Micro/6.0 -x podman-.*`

## Product list

```
$ susepkg -p list
RES-LTSS/7
RES/7
RES/8
SL-Micro/6.0
SL-Micro/6.1
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
SLED/15.7
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
SLES/15.7
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
SLES_SAP/15.7
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
SLE_RT/15.6
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
openSUSE_Leap/15.5
openSUSE_Leap/15.6
openSUSE_Leap_Micro/5.5
openSUSE_Leap_Micro/6.0
openSUSE_Tumbleweed
```
