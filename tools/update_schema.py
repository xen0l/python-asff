#!/usr/bin/env python

import argparse
import hashlib
import logging
import os
import subprocess
import sys
import urllib.request
from functools import partial
from typing import Union

log_level = logging.INFO
log_format = "%(message)s"
logging.basicConfig(level=log_level, format=log_format)

logger = logging.getLogger(__name__)

tools_dir = os.path.dirname(sys.argv[0])

SCHEMA_FILE = os.path.join(tools_dir, "service-2.json")
SCHEMA_URL = "https://raw.githubusercontent.com/boto/botocore/master/botocore/data/securityhub/2018-10-26/service-2.json"
GENERATE_CLASS = os.path.join(tools_dir, "generate_class.py")


def sha256sum(file: str, block_size: int = 2 ** 16) -> str:
    h = hashlib.new("sha256")
    with open(file, "rb") as f:
        for block in iter(partial(f.read, block_size), b""):
            h.update(block)
    return h.hexdigest()


def download_file(url: str, dest: str) -> None:
    urllib.request.urlretrieve(url=url, filename=dest)


def update_generated_asff_class() -> Union[
    subprocess.CompletedProcess, subprocess.CompletedProcess[bytes]
]:
    logger.info(f"Running {GENERATE_CLASS}...")
    return subprocess.run(GENERATE_CLASS)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--schema", default=SCHEMA_FILE, help="Security Hub schema file"
    )
    parser.add_argument("--url", default=SCHEMA_URL, help="Security Hub schema URL")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    schema_file = args.schema
    schema_url = args.url

    old_checksum = sha256sum(file=schema_file)

    try:
        download_file(url=schema_url, dest=schema_file)
    except Exception as e:
        logger.error(f"Error while downloading schema: {e}")
        exit(1)

    new_checksum = sha256sum(file=schema_file)

    logger.info(f"Old checksum: {old_checksum}")
    logger.info(f"New checksum: {new_checksum}")

    if old_checksum != new_checksum:
        update_generated_asff_class()
        logger.info("It is a good idea to review the changes")


if __name__ == "__main__":
    main()
