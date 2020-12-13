#!/usr/bin/env python
#
# This script is meant to be run when new security hub events are added or we need
# to regenerate sample securityhub event files
#

import json
import os

import boto3

# To get all supported TTPs, it's easiest to fetch it from the AWS console:
# https://eu-west-1.console.aws.amazon.com/securityhub/home?region=eu-west-1#/findings?search=ProductName%3D%255Coperator%255C%253AEQUALS%255C%253ASecurity%2520Hub&groupbyfield=Type
SUPPORTED_TTPS = {
    "Security Hub": [
        "Software and Configuration Checks/Industry and Regulatory Standards/CIS AWS Foundations Benchmark",
        "Software and Configuration Checks/Industry and Regulatory Standards/AWS-Foundational-Security-Best-Practices",
        "Effects/Data Exposure/AWS-Foundational-Security-Best-Practices",
    ],
    "Macie": [
        "Policy:IAMUser/S3BucketPublic",
        "Policy:IAMUser/S3BlockPublicAccessDisabled",
        "Policy:IAMUser/S3BucketSharedExternally",
        "Policy:IAMUser/S3BucketEncryptionDisabled",
    ],
    "IAM Access Analyzer": [
        "Software and Configuration Checks/AWS Security Best Practices/External Access Granted",
        "Effects/Data Exposure/External Access Granted",
    ],
    "Inspector": [
        "Software and Configuration Checks/AWS Security Best Practices/Network Reachability - Recognized port reachable from a Peered VPC",
        "Software and Configuration Checks/AWS Security Best Practices/Network Reachability - Network exposure from the internet",
        "Software and Configuration Checks/AWS Security Best Practices/Network Reachability - Recognized port with no listener reachable from internet",
        "Software and Configuration Checks/AWS Security Best Practices/Network Reachability - Network exposure from a Peered VPC",
        "Software and Configuration Checks/AWS Security Best Practices/Network Reachability - Recognized port reachable from internet",
        "Software and Configuration Checks/AWS Security Best Practices/Network Reachability - Recognized port with listener reachable from a Peered VPC",
        "Software and Configuration Checks/AWS Security Best Practices/Network Reachability - Recognized port with listener reachable from internet",
        "Software and Configuration Checks/AWS Security Best Practices/Network Reachability - Recognized port with no listener reachable from a Peered VPC",
        "Software and Configuration Checks/AWS Security Best Practices/Network Reachability - Unrecognized port with listener reachable from a Peered VPC",
        "Software and Configuration Checks/AWS Security Best Practices/Network Reachability - Unrecognized port with listener reachable from internet",
    ],
    "GuardDuty": [
        "TTPs/Command and Control/Backdoor:EC2-C&CActivity.B!DNS",
        "Software and Configuration Checks/Network Reachability/Recon:EC2-PortProbeUnprotectedPort",
        "TTPs/Initial Access/Recon:EC2-PortProbeUnprotectedPort",
        "TTPs/Defense Evasion/Stealth:IAMUser-CloudTrailLoggingDisabled",
        "Software and Configuration Checks/Policy:S3.BucketBlockPublicAccessDisabled",
        "Unusual Behaviors/User/UnauthorizedAccess:IAMUser-ConsoleLogin",
        "TTPs/Command and Control/Trojan:EC2-DGADomainRequest.B",
        "TTPs/Initial Access/UnauthorizedAccess:EC2-SSHBruteForce",
        "TTPs/Initial Access/Trojan:EC2-DriveBySourceTraffic!DNS",
        "Unusual Behaviors/User/Recon:IAMUser-UserPermissions",
        "TTPs/Command and Control/Trojan:EC2-BlackholeTraffic!DNS",
        "TTPs/Discovery/Recon:IAMUser-ResourcePermissions",
        "TTPs/Discovery/Recon:IAMUser-UserPermissions",
        "Unusual Behaviors/User/Recon:IAMUser-ResourcePermissions",
        "Effects/Data Exfiltration/Trojan:EC2-DropPoint!DNS",
        "Effects/Resource Consumption/CryptoCurrency:EC2-BitcoinTool.B!DNS",
        "TTPs/Command and Control/CryptoCurrency:EC2-BitcoinTool.B!DNS",
        "TTPs/Discovery/Recon:IAMUser-NetworkPermissions",
        "Unusual Behaviors/User/Recon:IAMUser-NetworkPermissions",
        "Effects/Data Exposure/Policy:S3-BucketBlockPublicAccessDisabled",
        "TTPs/Initial Access/Recon:EC2-Portscan",
        "Unusual Behaviors/VM/Behavior:EC2-NetworkPortUnusual",
        "TTPs/Command and Control/Trojan:EC2-DNSDataExfiltration!DNS",
        "TTPs/Discovery/Recon:EC2-Portscan",
        "TTPs/Command and Control/UnauthorizedAccess:EC2-TorIPCaller",
        "TTPs/Discovery/Recon:EC2-PortProbeUnprotectedPort",
        "TTPs/Persistence/Persistence:IAMUser-UserPermissions",
        "Software and Configuration Checks/Policy:S3.BucketAnonymousAccessGranted",
        "TTPs/Persistence/Persistence:IAMUser-NetworkPermissions",
        "Unusual Behaviors/User/Persistence:IAMUser-NetworkPermissions",
        "Unusual Behaviors/User/Persistence:IAMUser-UserPermissions",
        "Effects/Denial of Service/Backdoor:EC2-DenialOfService.UdpOnTcpPorts",
        "Effects/Resource Consumption/ResourceConsumption:IAMUser-ComputeResources",
        "Software and Configuration Checks/AWS Security Best Practices/Policy:IAMUser-RootCredentialUsage",
        "Unusual Behaviors/User/ResourceConsumption:IAMUser-ComputeResources",
        "Effects/Data Exfiltration/Trojan:EC2-DropPoint",
        "Effects/Data Exfiltration/UnauthorizedAccess:EC2-TorClient",
        "Effects/Data Exfiltration/UnauthorizedAccess:IAMUser-InstanceCredentialExfiltration",
        "Effects/Denial of Service/Backdoor:EC2-DenialOfService.Dns",
        "Effects/Denial of Service/Backdoor:EC2-DenialOfService.Tcp",
        "Effects/Denial of Service/Backdoor:EC2-DenialOfService.Udp",
        "Effects/Denial of Service/Backdoor:EC2-DenialOfService.UnusualProtocol",
        "Effects/Resource Consumption/CryptoCurrency:EC2-BitcoinTool.B",
        "Software and Configuration Checks/Network Reachability/Recon:EC2-PortProbeEMRUnprotectedPort",
        "Software and Configuration Checks/PrivilegeEscalation:IAMUser.AdministrativePermissions",
        "Software and Configuration Checks/Stealth:S3.ServerAccessLoggingDisabled",
        "Software and Configuration Checks/UnauthorizedAccess:EC2.MetadataDNSRebind",
        "TTPs/Command and Control/Backdoor:EC2-Spambot",
        "TTPs/Command and Control/CryptoCurrency:EC2-BitcoinTool.B",
        "TTPs/Command and Control/Trojan:EC2-BlackholeTraffic",
        "TTPs/Command and Control/Trojan:EC2-DGADomainRequest.C!DNS",
        "TTPs/Command and Control/Trojan:EC2-PhishingDomainRequest!DNS",
        "TTPs/Command and Control/UnauthorizedAccess:EC2-MaliciousIPCaller.Custom",
        "TTPs/Command and Control/UnauthorizedAccess:EC2-TorClient",
        "TTPs/Command and Control/UnauthorizedAccess:EC2-TorRelay",
        "TTPs/Command and Control/UnauthorizedAccess:IAMUser-TorIPCaller",
        "TTPs/Defense Evasion/Stealth:IAMUser-LoggingConfigurationModified",
        "TTPs/Defense Evasion/Stealth:IAMUser-PasswordPolicyChange",
        "TTPs/Discovery/PenTest:IAMUser-KaliLinux",
        "TTPs/Discovery/PenTest:IAMUser-ParrotLinux",
        "TTPs/Discovery/PenTest:IAMUser-PenTooLinux",
        "TTPs/Initial Access/Recon:EC2-PortProbeEMRUnprotectedPort",
        "TTPs/Initial Access/Recon:IAMUser-MaliciousIPCaller",
        "TTPs/Initial Access/Recon:IAMUser-MaliciousIPCaller.Custom",
        "TTPs/Initial Access/Recon:IAMUser-TorIPCaller",
        "TTPs/Initial Access/UnauthorizedAccess:EC2-RDPBruteForce",
        "TTPs/Persistence/Persistence:IAMUser-ResourcePermissions",
        "TTPs/UnauthorizedAccess:IAMUser-ConsoleLoginSuccess.B",
        "TTPs/UnauthorizedAccess:IAMUser-MaliciousIPCaller",
        "TTPs/UnauthorizedAccess:IAMUser-MaliciousIPCaller.Custom",
        "Unusual Behaviors/User/Persistence:IAMUser-ResourcePermissions",
        "Unusual Behaviors/User/Stealth:IAMUser-LoggingConfigurationModified",
        "Unusual Behaviors/VM/Backdoor:EC2-Spambot",
        "Unusual Behaviors/VM/Behavior:EC2-TrafficVolumeUnusual",
    ],
    "Systems Manager Patch Manager": [
        "Software & Configuration Checks/Patch Management/Compliance"
    ],
}


def download_seurityhub_findings(product_name, type, client=None, max_results=1):
    filters = {
        "ProductName": [{"Value": product_name, "Comparison": "EQUALS"}],
        "Type": [{"Value": type, "Comparison": "EQUALS"}],
    }

    kwargs = {
        "Filters": filters,
        "MaxResults": max_results,
    }

    findings = []
    paginator = client.get_paginator("get_findings")
    for page in paginator.paginate(**kwargs):
        findings.extend(page["Findings"])

        if len(findings) > 0:
            break

    if len(findings) > 0:
        return findings[0]
    else:
        return None


security_hub = boto3.client("securityhub", region_name="eu-west-1")

for product_name in SUPPORTED_TTPS:
    for ttp in SUPPORTED_TTPS[product_name]:
        print(f"Fetching {ttp} for {product_name}")

        normalized_product_name = product_name.replace(" ", "").lower()
        normalized_ttp = ttp.replace("/", "-")

        file = (
            "tests/data/events/{normalized_product_name}/{normalized_ttp}.json".format(
                normalized_product_name=normalized_product_name,
                normalized_ttp=normalized_ttp,
            )
        )

        finding = download_seurityhub_findings(
            product_name=product_name, type=ttp, client=security_hub
        )

        if finding:
            if not os.path.exists(os.path.dirname(file)):
                os.makedirs(os.path.dirname(file))
            print(f"Writing {file}")
            with open(file, "w") as f:
                data = json.dumps(finding, sort_keys=True, indent=4)
                f.write(data)
        else:
            print(f"No finding available for {ttp} for {product_name}")
            if os.path.exists(file):
                os.remove(file)
