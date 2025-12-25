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
from dataclasses import dataclass
from functools import cache, total_ordering

import rpm  # type: ignore
import requests
from requests.exceptions import RequestException

try:
    from requests_toolbelt.utils import dump  # type: ignore
except ImportError:
    dump = None


TIMEOUT = 180
VERSION = "2.2"

# Filter by this list of product identifiers
PRODUCTS = ("SLES/", "SLE-Micro/", "SL-Micro/", "SUSE-MicroOS/")
EOL = {
    "SLES/12",
    "SLES/12.1",
    "SLES/12.2",
    "SLES/12.3",
    "SLES/12.4",
    "SLES/15",
    "SLES/15.1",
    "SLES/15.2",
    "SLES/15.3",
    "SUSE-MicroOS/5.0",
    "SUSE-MicroOS/5.1",
}

session = requests.Session()


class Product(UserString):
    """
    Product class
    """

    def __init__(
        self, name: str, id_: int | None = None, arch: str | None = None
    ) -> None:
        self.data = name
        self.arch = arch
        self.id: int | None = None
        if "openSUSE" not in name:
            self.id = id_ or self._get_product_id(f"{name}/{arch}")
        super().__init__(name)

    @staticmethod
    @cache
    def _get_suse_products() -> dict | list[dict]:
        headers = {"Accept": "application/vnd.scc.suse.com.v4+json"}
        url = "https://scc.suse.com/api/package_search/products"
        return get_data(url, headers=headers)

    @classmethod
    def _get_product_id(cls, identifier: str) -> int:
        for product in cls._get_suse_products():
            if product["identifier"] == identifier:
                return product["id"]
        raise LookupError(f"Not found: {identifier}")

    @staticmethod
    @cache
    def _get_opensuse_products() -> list[dict]:
        headers = {"Accept": "application/json"}
        url = "https://get.opensuse.org/api/v0/distributions.json"
        data = get_data(url, headers=headers, key=None)
        assert isinstance(data, dict)
        return [
            {"name": item["name"].replace(" ", "_"), "version": item["version"]}
            for key, items in data.items()
            for i, item in enumerate(items)
            if item.get("state") == "Stable" or (key == "Tumbleweed" and i == 0)
        ]

    @classmethod
    def get_products(cls, arch: str) -> list["Product"]:
        """
        Get list of products
        """

        def product_sort_key(product: Product):
            """
            Group Micro's together
            """
            match = re.match(
                r"(SUSE-MicroOS|SLE-Micro|SL-Micro)/(\d+)\.(\d+)", product.data
            )
            if match:
                prefix, major, minor = match.groups()
                order = {"SUSE-MicroOS": 1, "SLE-Micro": 2, "SL-Micro": 3}
                return (1, order[prefix], int(major), int(minor))
            return (0, product.data)

        products = [
            cls(name=p["identifier"].removesuffix(f"/{arch}"), id_=p["id"], arch=arch)
            for p in cls._get_suse_products()
            if p["architecture"] == arch
            and p["identifier"].startswith(PRODUCTS)
            and p["identifier"].removesuffix(f"/{arch}") not in EOL
        ]
        products.sort(key=product_sort_key)
        products += sorted(
            cls(
                name=(
                    f'{p["name"]}/{p["version"]}'
                    if p["name"] != "openSUSE_Tumbleweed"
                    else p["name"]
                ),
                arch=arch,
            )
            for p in cls._get_opensuse_products()
        )
        return products


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


@dataclass(frozen=True)
class Package:
    """
    Package class
    """

    name: str
    product: str
    rpm_version: RPMVersion


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
    headers: dict | None = None,
    params: dict | None = None,
    key: str | None = "data",
) -> dict | list[dict]:
    """
    Get data from URL
    """
    try:
        got = session.get(url, headers=headers, params=params, timeout=TIMEOUT)
        got.raise_for_status()
    except RequestException as error:
        logging.error("%s: %s", url, error)
        raise
    data = got.json()
    return data[key] if key else data


def opensuse_package_info(info: dict) -> dict:
    """
    Get openSUSE package info
    """
    # Extract version & release from rpm filename
    version, release = info["file"].rsplit(".", 2)[0].rsplit("-", 2)[1:]
    return {
        "name": info["file"].split(f"-{version}-{release}")[0],
        "version": version,
        "release": release,
    }


def fetch_version(product: Product, package: str, regex: re.Pattern) -> list[Package]:
    """
    Fetch latest package version for the specified product
    """
    data: dict | list[dict]
    params: dict
    if product.startswith("openSUSE"):
        url = "https://mirrorcache.opensuse.org/rest/search/package_locations"
        headers = {"Accept": "application/json"}
        params = {
            # "arch": product.arch,
            "ignore_file": "json",
            "ignore_path": "/repositories/home:",
            "os": product.split("/")[0]
            .removeprefix("openSUSE_")
            .replace("_", "-")
            .lower(),
            "official": 1,
            "package": package,
        }
        if "/" in product:
            params["os_ver"] = product.split("/")[1]
        data = [
            opensuse_package_info(p)
            for p in get_data(url, headers=headers, params=params)
        ]
    else:
        url = "https://scc.suse.com/api/package_search/packages"
        headers = {"Accept": "application/vnd.scc.suse.com.v4+json"}
        params = {
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

    return [
        Package(
            name=name,
            product=product.data.removeprefix("openSUSE_"),
            rpm_version=rpm_version,
        )
        for name, rpm_version in latest.items()
    ]


def print_version(
    package_name: str, regex: re.Pattern, products: list[Product]
) -> None:
    """
    Print version
    """
    packages = []
    with ThreadPoolExecutor(max_workers=min(10, len(products))) as executor:
        futures = [
            executor.submit(fetch_version, product, package_name, regex)
            for product in products
        ]
        for future in futures:
            try:
                for package in future.result():
                    packages.append(package)
            except RequestException:
                pass
            except Exception as exc:  # pylint: disable=broad-exception-caught
                print(f"ERROR: {exc}", file=sys.stderr)
    package_width = 0
    product_width = 0
    for package in packages:
        package_width = max(package_width, len(package.name))
        product_width = max(product_width, len(package.product))
    fmt = f"{{:{product_width}}}  {{:{package_width}}}  {{}}"
    for package in packages:
        print(fmt.format(package.product, package.name, package.rpm_version))


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
    if string in {"Leap", "Leap_Micro", "Tumbleweed"}:
        return f"openSUSE_{string}"
    # Normalize multiple names for SLE Micro
    if "Micro" not in string or "Leap" in string:
        return string
    try:
        version = string.split("/", 1)[1]
        if int(version[0]) > 5:
            return f"SL-Micro/{version}"
    except IndexError:
        return string
    sub = int(version.split(".", 1)[1])
    if sub > 2:
        return f"SLE-Micro/{version}"
    return f"SUSE-MicroOS/{version}"


def parse_args() -> argparse.Namespace:
    """
    Parse args
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
        sys.exit(0)
    elif not args.package:
        parser.print_help()
        sys.exit(1)
    return args


def main() -> None:
    """
    Main function
    """
    args = parse_args()
    if args.product == ["any"]:
        args.product.pop()
    regex = get_regex(args.package, ignore_case=args.insensitive, regex=args.regex)
    package = get_name(args.package)
    if package is None:
        sys.exit(f"Invalid package: {args.package}")
    try:
        products = []
        all_products = Product.get_products(args.arch)
        if len(args.product) == 0:
            products = all_products
        else:
            for abbrev in args.product:
                # exact match first
                matched = [p for p in all_products if p.data == abbrev]
                if not matched:
                    # fallback: substring match (case-insensitive)
                    matched = [
                        p for p in all_products if abbrev.lower() in p.data.lower()
                    ]
                if not matched:
                    sys.exit(f"No matching product for: {abbrev}")
                products.extend(matched)
    except LookupError as exc:
        sys.exit(f"{exc}")
    except RequestException:
        sys.exit(1)
    print_version(package_name=package, regex=regex, products=products)


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
