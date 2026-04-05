#!/usr/bin/env python3
import os

import aws_cdk as cdk

from deploy.global_stack import GlobalStack
from deploy.deploy_stack import DeployStack

app = cdk.App()

account = os.getenv("CDK_DEFAULT_ACCOUNT")

global_stack = GlobalStack(app, "CertificateStack",
    env=cdk.Environment(account=account, region="us-east-1"),
    cross_region_references=True,
)

DeployStack(app, "DeployStack",
    certificate=global_stack.certificate,
    hosted_zone=global_stack.hosted_zone,
    web_acl_arn=global_stack.web_acl_arn,
    env=cdk.Environment(account=account, region=os.getenv("CDK_DEFAULT_REGION")),
    cross_region_references=True,
)

app.synth()
