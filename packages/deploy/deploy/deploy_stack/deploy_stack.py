from aws_cdk import (
    CfnOutput,
    Stack,
    aws_iam as iam,
)
from constructs import Construct
from deploy.deploy_stack.storage import Storage
from deploy.deploy_stack.data_storage import DataStorage
from deploy.deploy_stack.functions import EtlFunctions
from deploy.deploy_stack.events import Events
from deploy.deploy_stack.alerts import Alerts
from deploy.deploy_stack.queuing import Queuing
from deploy.deploy_stack.api import Api
from deploy.deploy_stack.cdn import Cdn
from deploy.deploy_stack.secrets import Secrets
from deploy.deploy_stack.vpc import Vpc

class DeployStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, certificate, hosted_zone, web_acl_arn, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        github_provider = iam.OpenIdConnectProvider(
                self, "GitHubProvider",
                url="https://token.actions.githubusercontent.com",
                client_ids=["sts.amazonaws.com"],
                thumbprints=["6938fd4d98bab03faadb97b34396831e3780aea1"]
            )

        provider_role = iam.Role(
            self, "GitHubActionRole",
            assumed_by=iam.OpenIdConnectPrincipal(
                github_provider,
                conditions={
                    "StringLike": {
                        "token.actions.githubusercontent.com:sub": "repo:dagda1/match-predictor:*"
                    }
                }
            ),
            description="Role assumed by GitHub Actions"
        )

        provider_role.add_to_policy(
            iam.PolicyStatement(
                actions=["sts:AssumeRole"],
                resources=[f"arn:aws:iam::{self.account}:role/cdk-hnb659fds-*"]
            )
        )

        provider_role.add_to_policy(
            iam.PolicyStatement(
                actions=["cloudformation:DescribeStacks"],
                resources=[self.stack_id]
            )
        )

        network = Vpc(self, "Network")

        storage = Storage(self, "Storage")
        DataStorage(self, "DataStorage", bucket=storage.bucket)
        functions=EtlFunctions(self, "EtlFunctions", bucket=storage.bucket)
        Queuing(self, "Queuing", scraper=functions.scraper, predictor=functions.predictor)
        Events(self, "EventBridge", scraper_function=functions.scraper)

        storage.frontend_bucket.grant_read_write(provider_role)

        app_secrets = Secrets(self, "Secrets")

        api = Api(self, "Api", bucket=storage.bucket, origin_verify_secret=app_secrets.origin_verify)

        Cdn(self, "Cdn",
            frontend_bucket=storage.frontend_bucket,
            certificate=certificate,
            hosted_zone=hosted_zone,
            http_api=api.http_api,
            origin_verify_secret=app_secrets.origin_verify.secret_value.unsafe_unwrap(),
            web_acl_arn=web_acl_arn,
        )

        CfnOutput(self, "FrontendBucketName", value=storage.frontend_bucket.bucket_name)