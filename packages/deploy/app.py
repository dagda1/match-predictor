#!/usr/bin/env python3
import os

import aws_cdk as cdk

from deploy.certificate_stack.edge_stack import EdgeStack
from deploy.deploy_stack.deploy_stack import DeployStack
from deploy.website_stack.website_stack import WebsiteStack

app = cdk.App()

account = os.getenv("CDK_DEFAULT_ACCOUNT")

WebsiteStack(app, "WebsiteStack",
      env=cdk.Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"],
  region="us-east-1"),
      cross_region_references=True,
  )

edge_stack = EdgeStack(app, "EdgeStack",
    env=cdk.Environment(account=account, region="us-east-1"),
    cross_region_references=True,
)

DeployStack(app, "DeployStack",
    certificate=edge_stack.certificate,
    hosted_zone=edge_stack.hosted_zone,
    web_acl_arn=edge_stack.web_acl_arn,
    env=cdk.Environment(account=account, region=os.getenv("CDK_DEFAULT_REGION")),
    cross_region_references=True,
)

app.synth()
