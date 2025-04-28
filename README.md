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
SLES/16.0
SUSE-MicroOS/5.0
SUSE-MicroOS/5.1
SUSE-MicroOS/5.2
SLE-Micro/5.3
SLE-Micro/5.4
SLE-Micro/5.5
SL-Micro/6.0
SL-Micro/6.1
SL-Micro/6.2
openSUSE_Leap/15.6
openSUSE_Leap_Micro/5.5
openSUSE_Leap_Micro/6.0
openSUSE_Leap_Micro/6.1
openSUSE_Tumbleweed
```
