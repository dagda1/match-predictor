#!/usr/bin/env python3
import os

import aws_cdk as cdk

from deploy.certificate_stack.global_stack import GlobalStack
from deploy.waf_stack.waf_stack import WafStack
from deploy.deploy_stack.deploy_stack import DeployStack

app = cdk.App()

account = os.getenv("CDK_DEFAULT_ACCOUNT")

global_stack = GlobalStack(app, "CertificateStack",
    env=cdk.Environment(account=account, region="us-east-1"),
    cross_region_references=True,
)

waf_stack = WafStack(app, "WafStack",
    env=cdk.Environment(account=account, region="us-east-1"),
)

DeployStack(app, "DeployStack",
    certificate=global_stack.certificate,
    hosted_zone=global_stack.hosted_zone,
    web_acl_arn=waf_stack.web_acl_arn,
    env=cdk.Environment(account=account, region=os.getenv("CDK_DEFAULT_REGION")),
    cross_region_references=True,
)

app.synth()
