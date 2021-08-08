# CLI utilities

python-asff comes with command line tools that make working with ASFF findings easier.

## asff-builder

_asff-builder_ allows the user to build ASFF finding from executing it from the command line. It is meant to be used mostly by the user or from the scripts.
Example use cases include running it from scripts and outputt   ing the finding in ASFF.

### Available options

```shell
usage: asff-builder [-h] --aws_account_id AWS_ACCOUNT_ID --types TYPES
                    [TYPES ...] --title TITLE --description DESCRIPTION
                    [--resources RESOURCES [RESOURCES ...]] [--id ID]
                    [--schema_version SCHEMA_VERSION] [--severity SEVERITY]
                    [--product_name PRODUCT_NAME]
                    [--product_version PRODUCT_VERSION] [--region REGION]
                    [--record_state RECORD_STATE]
                    [--workflow_status WORKFLOW_STATUS]
                    [--generator_id GENERATOR_ID] [--created_at CREATED_AT]
                    [--updated_at UPDATED_AT]

Simple tool to build ASFF findings from command line

optional arguments:
  -h, --help            show this help message and exit
  --aws_account_id AWS_ACCOUNT_ID
                        The AWS account ID that the finding applies to.
  --types TYPES [TYPES ...]
                        Finding type that classifies the finding
  --title TITLE         A finding's title.
  --description DESCRIPTION
                        A finding's description.
  --resources RESOURCES [RESOURCES ...]
                        A set of resource data types that describe the
                        resources that the finding refers to.
  --id ID               The identifier for the solution-specific component
                        that generated a finding.
  --schema_version SCHEMA_VERSION
                        The schema version that a finding is formatted for
  --severity SEVERITY   A finding's severity.
  --product_name PRODUCT_NAME
                        Product name that generated the finding
  --product_version PRODUCT_VERSION
                        Product version that generated the finding
  --region REGION       AWS region where the finding was found
  --record_state RECORD_STATE
                        The record state of a finding.
  --workflow_status WORKFLOW_STATUS
                        Provides information about the status of the
                        investigation into a finding.
  --generator_id GENERATOR_ID
                        The identifier for the solution-specific component
                        that generated a finding.
  --created_at CREATED_AT
                        Indicates when the potential security issue captured
                        by a finding was created.
  --updated_at UPDATED_AT
                        Indicates when the finding provider last updated the
                        finding record.

```

### Examples

#### Building ASFF JSON from the command line

```shell
% asff-builder --aws_account_id 1242334534 \
                --types 'TTPs/Defense Evasion' \
                --title 'Defense Evasion detected' \
                --description 'Defense Evastion detected on AWS account 1242334534' \
                --severity HIGH \
                --generator_id defense-evasion-detector
{
    "AwsAccountId": "1242334534",
    "CreatedAt": "2021-04-09T20:30:29+00:00",
    "Description": "Defense Evastion detected on AWS account 1242334534",
    "GeneratorId": "defense-evasion-detector",
    "Id": "c096c7ed402f02a78ee3dbecee25711595fd0bfbc2c77449d25fc173bf66f06d",
    "ProductArn": "arn:aws:securityhub:eu-west-1:1242334534:product/1242334534/default",
    "ProductFields": {
        "ProviderName": "default",
        "ProviderVersion": "1.0.0"
    },
    "RecordState": "ACTIVE",
    "Resources": [
        {
            "Id": "AWS::::Account:1242334534",
            "Partition": "aws",
            "Region": "eu-west-1",
            "Type": "AwsAccount"
        }
    ],
    "SchemaVersion": "2018-10-08",
    "Severity": {
        "Label": "HIGH"
    },
    "Title": "Defense Evasion detected",
    "Types": [
        "TTPs/Defense Evasion"
    ],
    "UpdatedAt": "2021-04-09T20:30:29+00:00",
    "Workflow": {
        "Status": "NEW"
    }
}
```

## asff-send

_asff-send_ is a utility to send ASFF findings directly to the Security Hub from the command line. It supports reading findings from a file or standard input, which is suitable for usage in shell pipelines.

### Available options

```shell
usage: asff-send [-h] [--region REGION] [--profile PROFILE] file

Utility to send ASFF findings to Security Hub easily from command line

positional arguments:
  file

optional arguments:
  -h, --help         show this help message and exit
  --region REGION    AWS region to use
  --profile PROFILE  AWS profile to use

```

### Examples

#### Sending finding to Security Hub from a file

```shell
% asff-builder --aws_account_id 1242334534 \
                --types 'TTPs/Defense Evasion' \
                --title 'Defense Evasion detected' \
                --description 'Defense Evastion detected on AWS account 1242334534' \
                --severity HIGH \ 
                --generator_id defense-evasion-detector > finding.json
% asff-send finding.json
```

#### Sending finding to Security Hub from standard input

```shell
% asff-builder --aws_account_id 1242334534 \
                --types 'TTPs/Defense Evasion' \
                --title 'Defense Evasion detected' \
                --description 'Defense Evastion detected on AWS account 1242334534' \
                --severity HIGH \ 
                --generator_id defense-evasion-detector | \
                asff-send --region eu-west-2 -
```