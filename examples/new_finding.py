#!/usr/bin/env python

from asff import AmazonSecurityFinding

f = AmazonSecurityFinding.from_kwargs(
    aws_account_id="0123456789012",
    title="Example finding",
    description="Example finding to demonstrate python-asff usage",
    types=["Software and Configuration Checks/AWS Security Best Practices"],
    product_name="python-asff-test",
)

print(f.to_json())
