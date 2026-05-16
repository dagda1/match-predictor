import hashlib
from pathlib import Path

from aws_cdk import (
    Arn,
    ArnComponents,
    ArnFormat,
    CustomResource,
    Duration,
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_lambda,
    aws_rds as rds,
)
from aws_cdk.custom_resources import Provider
from constructs import Construct

REPO_DIR = Path(__file__).resolve().parents[4]
MASTER_USER = "postgres"


def bootstrap_sql_hash() -> str:
    sql_path = REPO_DIR / "packages" / "db-bootstrap" / "sql" / "bootstrap.sql"
    return hashlib.sha256(sql_path.read_bytes()).hexdigest()


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
                "DB_HOST": database.db_instance_endpoint_address,
                "DB_NAME": "match_predictor",
                "DB_USER": MASTER_USER,
            },
        )

        stack = Stack.of(self)
        db_user_arn = Arn.format(
            components=ArnComponents(
                service="rds-db",
                resource="dbuser",
                resource_name=f"{database.instance_resource_id}/{MASTER_USER}",
                arn_format=ArnFormat.COLON_RESOURCE_NAME,
            ),
            stack=stack,
        )

        handler_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["rds-db:connect"],
                resources=[db_user_arn],
            )
        )

        provider = Provider(self, "Provider",
            on_event_handler=handler_function,
        )

        CustomResource(self, "Resource",
            service_token=provider.service_token,
            properties={"Version": bootstrap_sql_hash()},
        )
