from pathlib import Path

from aws_cdk import (
    CustomResource,
    Duration,
    aws_ec2 as ec2,
    aws_lambda,
    aws_rds as rds,
)
from aws_cdk.custom_resources import Provider
from constructs import Construct

REPO_DIR = Path(__file__).resolve().parents[4]

MIGRATOR_USER = "match_predictor_migrator"
APP_USER = "match_predictor_app"


class Bootstrap(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        database: rds.DatabaseInstance,
        vpc: ec2.Vpc,
        security_group: ec2.SecurityGroup,
    ) -> None:
        super().__init__(scope, construct_id)

        handler_function = aws_lambda.DockerImageFunction(self, "HandlerFunction",
            code=aws_lambda.DockerImageCode.from_image_asset(
                str(REPO_DIR / "packages" / "db-bootstrap"),
                file="Dockerfile",
                exclude=["__pycache__"],
            ),
            memory_size=256,
            timeout=Duration.minutes(5),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[security_group],
            ipv6_allowed_for_dual_stack=True,
            environment={
                "SECRET_ARN": database.secret.secret_arn,
                "DB_HOST": database.db_instance_endpoint_address,
                "DB_NAME": "match_predictor",
                "MIGRATOR_USER": MIGRATOR_USER,
                "APP_USER": APP_USER,
            },
        )

        database.secret.grant_read(handler_function)

        provider = Provider(self, "Provider",
            on_event_handler=handler_function,
        )

        CustomResource(self, "Resource",
            service_token=provider.service_token,
            properties={"Version": "1"},
        )
