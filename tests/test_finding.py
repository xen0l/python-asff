import glob
import json
import re

import pytest

from asff import AmazonSecurityFinding, ValidationError
from asff.constants import (
    DEFAULT_GENERATOR_ID,
    DEFAULT_PRODUCT_ARN_FMT,
    DEFAULT_REGION,
    DEFAULT_PRODUCT_NAME,
    DEFAULT_PRODUCT_VERSION,
    ISO8601_REGEX,
)
from asff.generated import Resource


@pytest.mark.parametrize(
    "path",
    glob.glob("**/events/*/*.json", recursive=True),
)
def test_finding_from_json(path):
    with open(path, "r") as f:
        data = f.read()
    expected_data = json.loads(data)

    finding = AmazonSecurityFinding.from_json(data)

    assert finding.to_json() == json.dumps(expected_data, sort_keys=True, indent=4)


@pytest.mark.parametrize(
    "path",
    glob.glob("**/events/*/*.json", recursive=True),
)
def test_finding_from_dict(path):
    with open(path, "r") as f:
        data = json.load(f)

    finding = AmazonSecurityFinding.from_dict(data)

    assert finding.to_dict() == data


@pytest.mark.parametrize(
    "path",
    glob.glob("**/events/*/*.json", recursive=True),
)
def test_finding_from_kwargs(path):
    with open(path, "r") as f:
        data = json.load(f)

    with open(path, "r") as f:
        expected_data = json.load(f)
        expected_finding = AmazonSecurityFinding.from_dict(expected_data)

    kwargs = {
        "aws_account_id": data["AwsAccountId"],
        "types": data["Types"],
        "title": data["Title"],
        "description": data["Description"],
        "resources": data["Resources"],
        "id": data["Id"],
        "schema_version": data["SchemaVersion"],
        "product_arn": data["ProductArn"],
        "generator_id": data["GeneratorId"],
        "updated_at": data["UpdatedAt"],
        "created_at": data["CreatedAt"],
        "severity": data["Severity"]["Label"],
    }

    attrs_to_delete = [
        "Types",
        "Title",
        "Description",
        "Resources",
        "Id",
        "SchemaVersion",
        "ProductArn",
        "GeneratorId",
        "UpdatedAt",
        "CreatedAt",
        "Severity",
    ]
    for attr in attrs_to_delete:
        del data[attr]

    kwargs.update(data)

    finding = AmazonSecurityFinding.from_kwargs(**kwargs)

    assert finding == expected_finding


def test_finding_from_kwargs_default_args():
    kwargs = {
        "aws_account_id": "12345678901",
        "title": "Title",
        "description": "Description",
        "types": ["TTP1"],
    }

    f = AmazonSecurityFinding.from_kwargs(**kwargs)

    assert re.match("^[a-f0-9]{64}$", f.id)
    assert f.product_arn == DEFAULT_PRODUCT_ARN_FMT.format(
        aws_account_id=kwargs["aws_account_id"],
        region=DEFAULT_REGION,
        product_name=DEFAULT_PRODUCT_NAME,
    )
    assert f.product_fields["ProviderName"] == DEFAULT_PRODUCT_NAME
    assert f.product_fields["ProviderVersion"] == DEFAULT_PRODUCT_VERSION
    assert f.generator_id == DEFAULT_GENERATOR_ID
    assert f.resources == [
        Resource(
            type="AwsAccount",
            id=f'AWS::::Account:{kwargs["aws_account_id"]}',
            partition="aws",
            region=DEFAULT_REGION,
            tags=None,
            details=None,
        )
    ]
    assert f.updated_at is not None
    assert f.created_at is not None
    assert re.match(ISO8601_REGEX, f.updated_at)
    assert re.match(ISO8601_REGEX, f.created_at)


@pytest.mark.parametrize(
    "time_attr", [{"created_at": "2020-22-12"}, {"updated_at": "2020-22-12"}]
)
def test_finding_from_kwargs_iso8601_timestamp_validation(time_attr):
    kwargs = {
        "aws_account_id": "12345678901",
        "title": "Title",
        "description": "Description",
        "types": ["TTP1"],
    }
    kwargs.update(time_attr)

    with pytest.raises(ValidationError):
        AmazonSecurityFinding.from_kwargs(**kwargs)


def test_finding_from_kwargs_predictable_id():
    kwargs = {
        "aws_account_id": "12345678901",
        "region": "eu-west-1",
        "title": "Title",
        "description": "Description",
        "types": ["TTP1"],
        "product_name": "python-asff",
    }

    f = AmazonSecurityFinding.from_kwargs(**kwargs)

    calculated_id = AmazonSecurityFinding.calculate_finding_id(
        aws_account_id=kwargs["aws_account_id"],
        region="eu-west-1",
        product_name=kwargs["product_name"],
        title=kwargs["title"],
    )

    assert f.id == calculated_id


def test_finding_equality(shared_datadir):

    e1 = (shared_datadir / "comparison" / "event1.json").read_text()
    e2 = (shared_datadir / "comparison" / "event2.json").read_text()

    f1 = AmazonSecurityFinding.from_json(e1)
    f2 = AmazonSecurityFinding.from_json(e2)
    f3 = AmazonSecurityFinding.from_json(e1)

    assert f1 == f3
    assert f1 != f2
    assert f1 != "random_string"


def test_finding_hashable(shared_datadir):

    e1 = (shared_datadir / "comparison" / "event1.json").read_text()
    e2 = (shared_datadir / "comparison" / "event2.json").read_text()

    f1 = AmazonSecurityFinding.from_json(e1)
    f2 = AmazonSecurityFinding.from_json(e2)
    f3 = AmazonSecurityFinding.from_json(e1)

    findings = [f1, f2, f3]
    d = {f1: "finding1", f2: "finding2", f3: "finding3"}

    assert set(findings)
    assert len(set(findings)) == 2

    assert d[f1]
    assert len(d.keys()) == 2
    assert d[f1] == "finding3"


@pytest.mark.parametrize(
    "path",
    glob.glob("**/broken_events/*.json", recursive=True),
)
def test_finding_exception(path):
    with open(path, "r") as f:
        data = json.load(f)

    with pytest.raises(ValidationError):
        AmazonSecurityFinding.from_dict(data)
