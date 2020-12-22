#!/usr/bin/env python

# flake8: noqa
import os
import argparse
import re
import sys

import json
import subprocess
from typing import List, Dict, Optional

import networkx as nx
from pydantic import BaseModel

tools_dir = os.path.dirname(sys.argv[0])

SCHEMA_FILE = os.path.join(tools_dir, "service-2.json")
CLASS_FILE = os.path.join(tools_dir, "../asff/generated.py")
HEADER_TEMPLATE = os.path.join(tools_dir, "class_header.template.py")

BASE_CLASS = "ASFFBaseModel"

classes = {}
type_aliases = {}
graph = nx.DiGraph()


# Some attributes are non-empty string, but have additional requirements, e.g. CreatedAt.
# We collect such cases here. Use the following command to build this:
#
# grep -B2 '<code>date-time</code>' tools/service-2.json | sed -Ee 's/"(.*)":{/"\1": "Iso8601Timestamp",/g' | grep Iso8601Timestamp | sort -u
#
TYPE_NORMALIZER = {
    "AttachTime": "Iso8601Timestamp",
    "ClusterCreateTime": "Iso8601Timestamp",
    "CreateDate": "Iso8601Timestamp",
    "CreateTime": "Iso8601Timestamp",
    "CreatedAt": "Iso8601Timestamp",
    "CreatedDate": "Iso8601Timestamp",
    "CreatedTime": "Iso8601Timestamp",
    "CreationDate": "Iso8601Timestamp",
    "CreationDateTime": "Iso8601Timestamp",
    "FirstObservedAt": "Iso8601Timestamp",
    "InaccessibleEncryptionDateTime": "Iso8601Timestamp",
    "InstanceCreateTime": "Iso8601Timestamp",
    "LastDecreaseDateTime": "Iso8601Timestamp",
    "LastIncreaseDateTime": "Iso8601Timestamp",
    "LastModified": "Iso8601Timestamp",
    "LastModifiedTime": "Iso8601Timestamp",
    "LastObservedAt": "Iso8601Timestamp",
    "LastUpdateToPayPerRequestDateTime": "Iso8601Timestamp",
    "LatestRestorableTime": "Iso8601Timestamp",
    "LaunchedAt": "Iso8601Timestamp",
    "OperationEndTime": "Iso8601Timestamp",
    "OperationStartTime": "Iso8601Timestamp",
    "RestoreDateTime": "Iso8601Timestamp",
    "SnapshotCreateTime": "Iso8601Timestamp",
    "TerminatedAt": "Iso8601Timestamp",
    "UpdateDate": "Iso8601Timestamp",
    "UpdatedAt": "Iso8601Timestamp",
    "VendorCreatedAt": "Iso8601Timestamp",
    "VendorUpdatedAt": "Iso8601Timestamp",
}


def normalize_type(member, type):
    return TYPE_NORMALIZER.get(member, type)


# Taken from https://github.com/jpvanhal/inflection/blob/master/inflection/__init__.py#L397-L416
# to avoid external dependency
def to_snake_case(word: str) -> str:  # pragma: no cover
    word = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", word)
    word = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", word)
    word = word.replace("-", "_")
    return word.lower()


def strip_html_tags(text):
    return re.sub("<[^<]+?>", "", text)


class Class(BaseModel):
    name: str
    required: List[str]
    attributes: List[Dict[str, str]]
    doc: Optional[str] = None

    def to_code(self):
        ret = [f"class {self.name}({BASE_CLASS}):"]
        if self.doc:
            ret.append('\t"""')
            ret.append(f"{strip_html_tags(self.doc)}")
            ret.append('\t"""')
        for attribute in self.attributes:
            for key, value in attribute.items():
                ret.append(f"\t{to_snake_case(key)}: {value}")

        return "\n".join(ret)


class TypeAlias(BaseModel):
    name: str
    type_hint: str

    def to_code(self):
        return f"{self.name} = {self.type_hint}"


def parse(name, schema):
    # TODO:
    # - add enum
    if schema[name]["type"] == "structure":
        required = schema[name].get("required", [])
        attributes = []
        docs = [schema[name].get("documentation"), ""]

        graph.add_node(name)

        if "members" in schema[name]:
            for member, type in schema[name]["members"].items():

                normalized_type = normalize_type(member, type["shape"])

                if member in required:
                    attributes.append({member: normalized_type})
                else:
                    attributes.append({member: f"Optional[{normalized_type}]"})

                if type.get("documentation"):
                    docs.append(
                        f':param {to_snake_case(member)}: {type["documentation"]}'
                    )

                graph.add_node(type["shape"])
                graph.add_edge(name, type["shape"])

                parse(type["shape"], schema)

        docs.extend(["", f":return: {name} object"])
        doc = "\n".join(docs)

        classes[name] = Class(
            name=name, required=required, attributes=attributes, doc=doc
        )

    else:
        type = schema[name]["type"]
        if type == "string":
            kwargs = {}
            if "pattern" in schema[name]:
                kwargs["regex"] = schema[name]["pattern"]
            if "min" in schema[name]:
                kwargs["min_length"] = int(schema[name]["min"])
            if "max" in schema[name]:
                kwargs["max_length"] = int(schema[name]["max"])
            if "enum" in schema[name]:
                kwargs["regex"] = "^({})$".format("|".join(schema[name]["enum"]))

            # Ensure that int values are not wrapped in quotes
            args_list = []
            for k, v in kwargs.items():
                if isinstance(v, int):
                    args_list.append(f"{k}={v}")
                else:
                    args_list.append(f'{k}="{v}"')
            args = ", ".join(args_list)

            type_hint = f"constr({args})"
            type_aliases[name] = TypeAlias(name=name, type_hint=type_hint)
            graph.add_node(name)

        elif type == "list":
            shape = schema[name]["member"]["shape"]

            type_hint = f"List[{shape}]"
            type_aliases[name] = TypeAlias(name=name, type_hint=type_hint)

            parse(shape, schema)

            graph.add_node(name)
            graph.add_node(shape)
            graph.add_edge(name, shape)

        elif type == "integer":
            type_hint = "int"
            type_aliases[name] = TypeAlias(name=name, type_hint=type_hint)

            graph.add_node(name)

        elif type == "map":
            key_type = schema[name]["key"]["shape"]
            value_type = schema[name]["value"]["shape"]

            type_hint = f"Dict[{key_type}, {value_type}]"
            type_aliases[name] = TypeAlias(name=name, type_hint=type_hint)

            graph.add_node(name)

        elif type == "double":
            # We have int here on purpose as most fields marked as double are not
            # printed with decimal point. We want to avoid that by using int.
            type_hint = "int"
            type_aliases[name] = TypeAlias(name=name, type_hint=type_hint)

            graph.add_node(name)

        elif type == "boolean":
            type_hint = "bool"
            type_aliases[name] = TypeAlias(name=name, type_hint=type_hint)

            graph.add_node(name)

        elif type == "long":
            type_hint = "int"
            type_aliases[name] = TypeAlias(name=name, type_hint=type_hint)

            graph.add_node(name)
        else:
            print(f"UNKNOWN TYPE: {type}")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--schema-file", default=SCHEMA_FILE, help="Path to AWS Secuity Hub schema"
    )
    parser.add_argument(
        "--class-file", default=CLASS_FILE, help="Path to generated file in library"
    )
    parser.add_argument(
        "--header-file",
        default=HEADER_TEMPLATE,
        help="Path to generated file header template",
    )
    parser.add_argument(
        "--base-class",
        default=BASE_CLASS,
        help="Default class that all generated classes inheit from",
    )

    return parser.parse_args()


def main():

    args = parse_arguments()

    data = {}
    with open(SCHEMA_FILE, "r") as f:
        data = json.load(f)

    parse("AwsSecurityFinding", data["shapes"])

    dependencies = list(reversed(list(nx.topological_sort(graph))))

    python_file = []
    with open(HEADER_TEMPLATE, "r") as f:
        for line in f:
            line = line.rstrip()
            python_file.append(line)

    for item in dependencies:
        if item in type_aliases:
            python_file.append(type_aliases[item].to_code())
        else:
            python_file.append(classes[item].to_code())

    ret = subprocess.run(
        ["black", "-"], input="\n".join(python_file).encode(), capture_output=True
    )

    with open(CLASS_FILE, "w") as f:
        f.write(ret.stdout.decode())


if __name__ == "__main__":
    main()
