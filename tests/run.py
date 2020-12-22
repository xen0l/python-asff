#!/usr/bin/env python

import argparse
import os
import sys

parser = argparse.ArgumentParser()
parser.add_argument(
    "-L",
    "--no-lint",
    action="store_false",
    default=True,
    dest="lint",
    help="Skip file linting",
)
parser.add_argument(
    "-C",
    "--no-coverage",
    action="store_false",
    default=True,
    dest="coverage",
    help="Skip coverage report",
)
args, rest = parser.parse_known_args()

root_dir = os.path.abspath(os.path.split(os.path.dirname(sys.argv[0]))[0])
report_dir = os.path.join(root_dir, "reports")

if not os.path.exists(report_dir):
    os.mkdir(report_dir, mode=0o755)

cmd = ["poetry", "run", "pytest", "--verbose"]

if args.lint:
    lint_args = [
        "--flake8",
        "--black",
        "--pylint",
        "--pylint-rcfile={}".format(os.path.join(root_dir, ".pylintrc")),
        "--pylint-ignore-patterns=tools,docs,examples",
    ]
    cmd.extend(lint_args)

if args.coverage:
    coverage_args = [
        "--cov=asff",
        "--cov-fail-under=100",
        "--cov-report=term-missing",
        "--cov-report=xml:{}".format(os.path.join(report_dir, "coverage.xml")),
        "--cov-report=html:{}".format(os.path.join(report_dir, "coverage", "asff")),
        "--junitxml={}".format(os.path.join(report_dir, "test.xml")),
    ]
    cmd.extend(coverage_args)
else:
    cmd.append("--no-cov")

cmd.extend(rest)

os.execvp(cmd[0], cmd)  # noqa: S606
