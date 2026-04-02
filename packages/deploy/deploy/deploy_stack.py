from aws_cdk import (
    CfnOutput,
    Stack,
    aws_iam as iam,
)
from constructs import Construct
from deploy.storage import Storage
from deploy.data_storage import DataStorage
from deploy.etl.functions import EtlFunctions
from deploy.events import Events
from deploy.alerts import Alerts
from deploy.queuing import Queuing

class DeployStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
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

        storage = Storage(self, "Storage")
        DataStorage(self, "DataStorage", bucket=storage.bucket)
        functions=EtlFunctions(self, "EtlFunctions", bucket=storage.bucket)
        Queuing(self, "Queuing", scraper=functions.scraper, predictor=functions.predictor)
        Events(self, "EventBridge", scraper_function=functions.scraper)

        storage.frontend_bucket.grant_read_write(provider_role)

        CfnOutput(self, "FrontendBucketName", value=storage.frontend_bucket.bucket_name)