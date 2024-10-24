#!/usr/bin/env python3
"""
Show SUSE package versions
"""

import argparse
import fnmatch
import logging
import platform
import re
import os
import sys
from collections import UserString
from concurrent.futures import ThreadPoolExecutor
from functools import cache, total_ordering

import rpm  # type: ignore
import requests
from requests.exceptions import RequestException

try:
    from requests_toolbelt.utils import dump  # type: ignore
except ImportError:
    dump = None


TIMEOUT = 180
VERSION = "1.2"

session = requests.Session()


class Product(UserString):
    """
    Product class
    """

    def __init__(
        self, name: str, id_: int | None = None, arch: str | None = None
    ) -> None:
        self.data = name
        self.id = id_ or self._get_product_id(f"{name}/{arch}")
        super().__init__(name)

    @staticmethod
    @cache
    def _get_products() -> list[dict]:
        headers = {"Accept": "application/vnd.scc.suse.com.v4+json"}
        url = "https://scc.suse.com/api/package_search/products"
        return get_data(url, headers=headers)

    @classmethod
    def _get_product_id(cls, identifier: str) -> int:
        for product in cls._get_products():
            if product["identifier"] == identifier:
                return product["id"]
        raise LookupError(f"Not found: {identifier}")

    @classmethod
    def get_products(cls, arch: str) -> list["Product"]:
        """
        Get list of products
        """
        return sorted(
            cls(name=p["identifier"].removesuffix(f"/{arch}"), id_=p["id"], arch=arch)
            for p in cls._get_products()
            if p["architecture"] == arch
        )


@total_ordering
class RPMVersion:
    """
    RPMVersion class to compare RPM versions
    """

    def __init__(self, version: str, release: str) -> None:
        self.version = version
        self.release = release
        self._tuple = ("1", version, release)

    def __str__(self) -> str:
        return f"{self.version}-{self.release}"

    def __lt__(self, other) -> bool:
        # pylint: disable=no-member
        return rpm.labelCompare(self._tuple, other._tuple) < 0

    def __eq__(self, other) -> bool:
        # pylint: disable=no-member
        return rpm.labelCompare(self._tuple, other._tuple) == 0


def debugme(got, *args, **kwargs):  # pylint: disable=unused-argument
    """
    Print requests response
    """
    got.hook_called = True
    if dump is not None:
        print(dump.dump_all(got).decode("utf-8"), file=sys.stderr)
    return got


def get_data(
    url: str,
    headers: dict[str, str] | None = None,
    params: dict[str, str | int] | None = None,
) -> list[dict]:
    """
    Get data from URL
    """
    try:
        got = session.get(url, headers=headers, params=params, timeout=TIMEOUT)
        got.raise_for_status()
    except RequestException as error:
        logging.error("%s: %s", url, error)
        raise
    return got.json()["data"]


def fetch_version(product: Product, package: str, regex: re.Pattern) -> list[str]:
    """
    Fetch latest package version for the specified product
    """
    url = "https://scc.suse.com/api/package_search/packages"
    headers = {"Accept": "application/vnd.scc.suse.com.v4+json"}
    params: dict[str, str | int] = {
        "query": package,
        "product_id": product.id,
    }
    data = get_data(url, headers=headers, params=params)

    latest: dict[str, RPMVersion] = {}
    for info in sorted(
        filter(lambda i: regex.match(i["name"]), data),
        key=lambda i: (i["name"], RPMVersion(i["version"], i["release"])),
    ):
        latest[info["name"]] = RPMVersion(info["version"], info["release"])

    return [f"{product} {name} {rpm_version}" for name, rpm_version in latest.items()]


def print_version(
    package: str, arch: str, regex: re.Pattern, product_list: list[str]
) -> None:
    """
    Print version
    """
    try:
        if len(product_list) == 0:
            products = Product.get_products(arch)
        else:
            products = [Product(name=product, arch=arch) for product in product_list]
    except LookupError as exc:
        sys.exit(f"{exc}")
    except RequestException:
        sys.exit(1)

    with ThreadPoolExecutor(max_workers=min(10, len(products))) as executor:
        futures = [
            executor.submit(fetch_version, product, package, regex)
            for product in products
        ]
        for future in futures:
            try:
                lines = future.result()
                for line in lines:
                    print(line)
            except RequestException:
                pass
            except Exception as exc:  # pylint: disable=broad-exception-caught
                print(f"ERROR: {exc}", file=sys.stderr)


def get_regex(
    package: str, ignore_case: bool = False, regex: bool = False
) -> re.Pattern:
    """
    Compile package string to regular expression
    """
    flags = re.IGNORECASE if ignore_case else 0
    if regex:
        return re.compile(package, flags)
    if any(c in package for c in "[?*"):
        return re.compile(fnmatch.translate(package), flags)
    return re.compile(f"{package}$", flags)


def get_name(string: str) -> str | None:
    """
    Get package name from string that may be a regular expression
    """
    pattern = r"[\w-]+"
    matches = re.findall(pattern, string, re.ASCII)
    if matches:
        return max(matches, key=len)
    return None


def product_string(string: str) -> str:
    """
    Normalize product strings
    """
    if "Micro" not in string:
        return string
    version = string.split("/", 1)[1]
    if int(version[0]) > 5:
        return f"SL-Micro/{version}"
    sub = int(version.split(".", 1)[1])
    if sub > 2:
        return f"SLE-Micro/{version}"
    return f"SUSE-MicroOS/{version}"


def main() -> None:
    """
    Main function
    """
    parser = argparse.ArgumentParser(
        prog="susepkg",
        description="show SUSE package versions",
    )
    parser.add_argument(
        "-a",
        "--arch",
        choices=["aarch64", "ppc64le", "s390x", "x86_64"],
        default=platform.machine(),
    )
    parser.add_argument(
        "-i", "--insensitive", action="store_true", help="case insensitive search"
    )
    parser.add_argument(
        "-p",
        "--product",
        action="append",
        required=True,
        type=product_string,
        help="product or 'list' or 'any'. May be specified multiple times",
    )
    parser.add_argument(
        "-x", "--regex", action="store_true", help="search regular expression"
    )
    parser.add_argument("--version", action="version", version=f"v{VERSION}")
    parser.add_argument(
        "package", nargs="?", help="may be a shell pattern or regular expression"
    )
    args = parser.parse_args()

    if args.product == ["list"]:
        for product in Product.get_products(args.arch):
            print(product)
    elif not args.package:
        parser.print_help()
        sys.exit(1)
    else:
        if args.product == ["any"]:
            args.product.pop()
        regex = get_regex(args.package, ignore_case=args.insensitive, regex=args.regex)
        package = get_name(args.package)
        if package is None:
            sys.exit(f"Invalid package: {args.package}")
        print_version(
            package=package, arch=args.arch, regex=regex, product_list=args.product
        )


if __name__ == "__main__":
    if os.getenv("DEBUG"):
        session.hooks["response"].append(debugme)
    logging.basicConfig(format="%(levelname)-8s %(message)s", stream=sys.stderr)
    try:
        main()
    except KeyboardInterrupt:
        session.close()
        sys.exit(1)
    finally:
        session.close()
