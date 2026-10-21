import argparse

import boto3
import requests
from botocore.exceptions import ClientError

PROFILE = "nds-sg-access-dev"
GROUP_ID = "sg-0e9c19f7b069c2b73"
PORT = 5439
LABEL = "nds-airflow"


def rule(cidr, label=None):
    ip_range = {"CidrIp": cidr}
    if label:
        ip_range["Description"] = label
    return [{"IpProtocol": "tcp", "FromPort": PORT, "ToPort": PORT, "IpRanges": [ip_range]}]


def open_access(ec2):
    ip = requests.get("https://checkip.amazonaws.com", timeout=10).text.strip()
    try:
        ec2.authorize_security_group_ingress(GroupId=GROUP_ID, IpPermissions=rule(f"{ip}/32", LABEL))
        print(f"added {ip}")
    except ClientError as e:
        if e.response["Error"]["Code"] != "InvalidPermission.Duplicate":
            raise
        print(f"{ip} already allowed")


def close_access(ec2):
    rules = ec2.describe_security_group_rules(
        Filters=[{"Name": "group-id", "Values": [GROUP_ID]}]
    )["SecurityGroupRules"]
    for r in rules:
        if not r["IsEgress"] and r.get("Description") == LABEL:
            ec2.revoke_security_group_ingress(GroupId=GROUP_ID, IpPermissions=rule(r["CidrIpv4"]))
            print(f"removed {r['CidrIpv4']}")


parser = argparse.ArgumentParser()
parser.add_argument("action", choices=["open", "close"])
args = parser.parse_args()

ec2 = boto3.Session(profile_name=PROFILE).client("ec2")
if args.action == "open":
    open_access(ec2)
else:
    close_access(ec2)