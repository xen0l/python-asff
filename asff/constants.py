import os

DEFAULT_REGION = os.environ.get("AWS_DEFAULT_REGION", "eu-west-1")

DEFAULT_SCHEMA_VERSION = "2018-10-08"
DEFAULT_SEVERITY = "MEDIUM"
DEFAULT_PRODUCT_ARN_FMT = "arn:aws:securityhub:{region}:{aws_account_id}:product/{aws_account_id}/{product_name}"  # noqa: B950
DEFAULT_PRODUCT_NAME = "default"
DEFAULT_PRODUCT_VERSION = "1.0.0"
DEFAULT_GENERATOR_ID = "GeneratorId"
DEFAULT_RECORD_STATE = "ACTIVE"
DEFAULT_WORKFLOW_STATUS = "NEW"
