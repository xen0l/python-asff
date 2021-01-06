# Overview

## Motivation

I run security operations in multi-account AWS organization setup. There are various AWS & open source security tools used for handling security events in AWS. 
However, I found it very beneficial to centralize all findings in [AWS Security Hub](https://aws.amazon.com/security-hub/) as it provides complete overview of all
security events in the AWS organization. Apart from that, it also normalizes all security events into a common format: [Amazon Security Finding Format (ASFF)](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-findings-format.html).

The benefit of this is that regardless of vendor or tool, all the findings share the same format. However, there are some downsides:

* the format is quite extensive (which is DEFINITELY good for verbose information, but can cause headaches what and how much data should be provided)
* there are no easy to use libraries with proper validation and simple interface
* lack of tooling to build ASFF findings regardless of the programming language

*python-asff* tries to rectify this.

## Main features

python-asff main features are:

* **schema correctness** - once Python class has been created, it will be fully validated, so user can be certain that class is always 
  suitable for ingestion into AWS Security Hub.
* **simplicity** - the library aims to provide extremely simple interface, so people can ingest finding easily and focus on what matters - fixing them. 
  Moreover, it also provides helpers that allow you to fetch information about resources easily.
* **minimal dependencies** - for as wider adoption as possible, we commit to keep the number of external dependencies very small. 
  Only dependency to stay is [pydantic](https://github.com/samuelcolvin/pydantic), which provides underlying functionality. 
* **CLI tooling** - provide CLI tooling that will allow non-Python projects to create ASFF findings from any security tool suitable 
  for ingestion into Security Hub easily.