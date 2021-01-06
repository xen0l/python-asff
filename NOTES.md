# Interesting read

## Security Hub custom providers

* https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-custom-providers.html

## Security Hub finding updates

Security Hub findings can be updated. However, there are some limitations on which attributes can be updated 
and one should be aware of them. The list can be found [here](https://docs.aws.amazon.com/securityhub/latest/userguide/finding-update-batchupdatefindings.html#batchupdatefindings-fields).

## Findings discovered while working with Security Hub

### CreatedAt and UpdatedAt ISO 8601 check

Security Hub schema states that CreatedAt, UpdatedAt and similar fields should follow `date-time` from [RFC 3339](https://tools.ietf.org/html/rfc3339#section-5.6).
However, the schema defines this type as non-empty string. Secuity Hub API returned the following regular expression:

```
(\\d\\d\\d\\d)-[0-1](\\d)-[0-3](\\d)[Tt](?:[0-2](\\d):[0-5](\\d):[0-5](\\d)|23:59:60)(?:\\.(\\d)+)?(?:[Zz]|[+-](\\d\\d)(?::?(\\d\\d))?)$
```

### Resources in AwsSecurityFinding cannot be an empty list

Security Hub schema does not seem to mention anything about requiring at least one resouce in Resources.
Sample error response:

```json
{
    "FailedCount": 1,
    "FailedFindings": [
        {
            "ErrorCode": "InvalidInput",
            "ErrorMessage": "Finding does not adhere to Amazon Finding Format. data.Resources should NOT have fewer than 1 items.",
            "Id": "69b19573-f60c-45f4-bad7-cc39c98dad92"
        }
    ],
    "ResponseMetadata": {
        "HTTPHeaders": {
            "connection": "keep-alive",
            "content-length": "244",
            "content-type": "application/json",
            "date": "Tue, 22 Dec 2020 18:55:23 GMT",
            "x-amz-apigw-id": "X98cTGGnDoEFbEg=",
            "x-amzn-requestid": "20359099-5dbd-4652-ac0c-ed2aa031a224",
            "x-amzn-trace-id": "Root=1-5fe2411b-7f834d21130461413669ff32"
        },
        "HTTPStatusCode": 200,
        "RequestId": "20359099-5dbd-4652-ac0c-ed2aa031a224",
        "RetryAttempts": 0
    },
    "SuccessCount": 0
}
```

It seems that the sensible default is `AwsAccount`. 