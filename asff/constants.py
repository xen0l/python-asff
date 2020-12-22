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

ISO8601_REGEX = r"(\d\d\d\d)-[0-1](\d)-[0-3](\d)[Tt](?:[0-2](\d):[0-5](\d):[0-5](\d)|23:59:60)(?:\.(\d)+)?(?:[Zz]|[+-](\d\d)(?::?(\d\d))?)$"  # noqa: B950
