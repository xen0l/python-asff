import hashlib
import inspect
import json
from datetime import datetime, timezone
from typing import List, Any, Optional, Dict

import pydantic

from asff.constants import (
    DEFAULT_SEVERITY,
    DEFAULT_SCHEMA_VERSION,
    DEFAULT_PRODUCT_ARN_FMT,
    DEFAULT_REGION,
    DEFAULT_GENERATOR_ID,
    DEFAULT_PRODUCT_NAME,
    DEFAULT_PRODUCT_VERSION,
    DEFAULT_RECORD_STATE,
    DEFAULT_WORKFLOW_STATUS,
)
from asff.exceptions import ValidationError
from asff.generated import AwsSecurityFinding, TypeList, NonEmptyString, Resource


class AmazonSecurityFinding(AwsSecurityFinding):
    def __init__(self, **data):
        try:
            super().__init__(**data)
        except pydantic.ValidationError as e:
            raise ValidationError(e) from None

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        return NotImplemented

    def __dir__(self):  # pragma: no cover
        pydantic_methods = [
            func
            for func, _ in inspect.getmembers(
                AwsSecurityFinding, predicate=inspect.ismethod
            )
        ]

        self_methods = [
            func
            for func, _ in inspect.getmembers(
                AmazonSecurityFinding, predicate=inspect.ismethod
            )
        ]

        self_vars = list(vars(self).keys())

        return list(set(self_methods) - set(pydantic_methods)) + dir(object) + self_vars

    def to_json(self) -> str:
        """
        Return a JSON representation of the finding.

        :return: JSON representation of the finding
        """
        return self.json(exclude_unset=True, by_alias=True, indent=4, sort_keys=True)

    def to_dict(self) -> Dict[str, Any]:
        """
        Return a dict representation of the finding.

        :return: A dict representation of the finding
        """
        return self.dict(exclude_unset=True, by_alias=True)

    @staticmethod
    def calculate_finding_id(
        aws_account_id: str, region: str, product_name: str, title: str
    ) -> str:
        """
        Calculate predictable unique finding ID based on immutable finding attributes.
        The finding ID is calculated as a SHA256 hash of the string consisting of the following
        attributes:
        - aws_account_id
        - region
        - product_name
        - title

        finding_id = SHA256(aws_account_id + region + product_name + title)

        In the future, the list of attributes used for calculating hashes might be extended, but the
        primary purpose is to have a set of attributes that are unique, yet easy to remember, so the
        finding ID could be calculated easily and found by this library.

        :param aws_account_id: The AWS account ID that the finding applies to.
        :param region: AWS region where the finding was found
        :param product_name: Product name that generated the finding
        :param title: A finding's title.

        :return: A predictable unique finding ID
        """

        attrs = [aws_account_id, region, product_name, title]
        string = "+".join(attrs).encode()

        h = hashlib.new("sha256")
        h.update(string)

        return h.hexdigest()

    @classmethod
    def from_kwargs(
        cls,
        aws_account_id: str,
        types: TypeList,
        title: NonEmptyString,
        description: NonEmptyString,
        resources: Optional[List[Any]] = None,
        id: Optional[str] = None,  # pylint: disable=redefined-builtin
        schema_version: str = DEFAULT_SCHEMA_VERSION,
        severity: str = DEFAULT_SEVERITY,
        product_name: Optional[str] = DEFAULT_PRODUCT_NAME,
        product_version: Optional[str] = DEFAULT_PRODUCT_VERSION,
        region: str = DEFAULT_REGION,
        record_state: str = DEFAULT_RECORD_STATE,
        workflow_status: str = DEFAULT_WORKFLOW_STATUS,
        generator_id: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        **kwargs,
    ):
        """
        Construct the finding from keyword arguments.

        :param aws_account_id: The AWS account ID that the finding applies to.
        :param types: Finding type that classifies the finding
        :param title: A finding's title.
        :param description: A finding's description.
        :param resources: A set of resource data types that describe the resources that the finding refers to.
        :param id: The product-specific identifier for a finding.
        :param schema_version: The schema version that a finding is formatted for
        :param severity: A finding's severity.
        :param product_name: Product name that generated the finding
        :param product_version: Product version that generated the finding
        :param region: AWS region where the finding was found
        :param record_state: The record state of a finding.
        :param workflow_status: Provides information about the status of the investigation into a finding.
        :param generator_id: The identifier for the solution-specific component that generated a finding.
        :param created_at: Indicates when the potential security issue captured by a finding was created.
        :param updated_at: Indicates when the finding provider last updated the finding record.
        :param kwargs: Additional keyword arguments, suitable for passing fields such as notes, user_defined_fields etc
        :return: A finding object
        """
        if id is None:
            id = cls.calculate_finding_id(
                aws_account_id=aws_account_id,
                region=region,
                product_name=product_name,
                title=title,
            )

        if generator_id is None:
            generator_id = DEFAULT_GENERATOR_ID

        if resources is None:
            resources = [
                Resource(
                    type="AwsAccount",
                    id=f"AWS::::Account:{aws_account_id}",
                    region=region,
                    partition="aws",
                )
            ]

        if created_at is None:
            created_at = str(
                datetime.now(tz=timezone.utc).isoformat(timespec="seconds")
            )

        if updated_at is None:
            updated_at = str(
                datetime.now(tz=timezone.utc).isoformat(timespec="seconds")
            )

        product_arn = DEFAULT_PRODUCT_ARN_FMT.format(
            region=region,
            aws_account_id=aws_account_id,
            product_name=DEFAULT_PRODUCT_NAME,
        )

        # Required arguments
        kwargs["AwsAccountId"] = aws_account_id
        kwargs["Types"] = types
        kwargs["Title"] = title
        kwargs["Description"] = description
        kwargs["Resources"] = resources
        kwargs["Id"] = id
        kwargs["SchemaVersion"] = schema_version
        kwargs["ProductArn"] = product_arn
        kwargs["GeneratorId"] = generator_id
        kwargs["UpdatedAt"] = updated_at
        kwargs["CreatedAt"] = created_at
        kwargs["Severity"] = {"Label": severity}

        # Other sensible defaults
        kwargs["RecordState"] = record_state
        kwargs["Workflow"] = {"Status": workflow_status}

        product_description = {
            "ProviderName": product_name,
            "ProviderVersion": product_version,
        }
        if "ProductFields" in kwargs:
            kwargs["ProductFields"].update(product_description)
        else:
            kwargs["ProductFields"] = product_description

        return cls(**kwargs)

    @classmethod
    def from_dict(cls, data) -> "AmazonSecurityFinding":
        """
        Construct the finding from a dictionary.

        :param data: Dictionary holding finding data
        :return: A finding object
        """
        return cls(**data)

    @classmethod
    def from_json(cls, data: str) -> "AmazonSecurityFinding":
        """
        Construct the finding from a JSON string.

        :param data: JSON string with finding data
        :return: A finding object
        """
        kwargs = json.loads(data)

        return cls(**kwargs)
