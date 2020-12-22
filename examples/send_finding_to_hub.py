#!/usr/bin/env python

import json

import boto3

from asff import AmazonSecurityFinding

sts = boto3.client("sts")
aws_account_id = sts.get_caller_identity()["Account"]

f = AmazonSecurityFinding.from_kwargs(
    aws_account_id=aws_account_id,
    title="Example finding",
    description="Example finding to demonstrate python-asff usage",
    types=["Software and Configuration Checks/AWS Security Best Practices"],
    product_name="python-asff-test",
)

sh = boto3.client("securityhub", region_name="eu-west-1")
response = sh.batch_import_findings(Findings=[f.to_dict()])

print(json.dumps(response, indent=4, sort_keys=True))
