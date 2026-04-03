#!/usr/bin/env python3
import os

import aws_cdk as cdk

from deploy.certificate import CertificateStack
from deploy.deploy_stack import DeployStack

app = cdk.App()

account = os.getenv("CDK_DEFAULT_ACCOUNT")

cert_stack = CertificateStack(app, "CertificateStack",
    env=cdk.Environment(account=account, region="us-east-1"),
    cross_region_references=True,
)

DeployStack(app, "DeployStack",
    certificate=cert_stack.certificate,
    hosted_zone=cert_stack.hosted_zone,
    env=cdk.Environment(account=account, region=os.getenv("CDK_DEFAULT_REGION")),
    cross_region_references=True,
)

app.synth()
