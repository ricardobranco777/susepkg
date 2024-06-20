# susepkg

Show SUSE package versions

## Requirements

- Python 3.11+

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
usage: susepkg [-h] [-a] [-A {aarch64,ppc64le,s390x,x86_64}] [--debug]
               [-p PRODUCT]
               package

show SUSE package versions

positional arguments:
  package

options:
  -h, --help            show this help message and exit
  -a, --all
  -A {aarch64,ppc64le,s390x,x86_64}, --arch {aarch64,ppc64le,s390x,x86_64}
  --debug
  -p PRODUCT, --product PRODUCT
```
