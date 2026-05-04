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

from deploy.deploy_stack.database_users import MIGRATOR_USER

REPO_DIR = Path(__file__).resolve().parents[4]


def alembic_versions_hash() -> str:
    versions_dir = REPO_DIR / "packages" / "ml" / "alembic" / "versions"
    hasher = hashlib.sha256()

    for path in sorted(versions_dir.glob("*.py")):
        hasher.update(path.read_bytes())

    return hasher.hexdigest()


class Migration(Construct):
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
                str(REPO_DIR),
                file="packages/ml/migration.Dockerfile",
                exclude=[
                    "__pycache__",
                    ".venv",
                    "node_modules",
                    ".turbo",
                    "**/cdk.out",
                    ".git",
                    "dist",
                    "*.pyc",
                ],
            ),
            memory_size=512,
            timeout=Duration.minutes(5),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[security_group],
            environment={
                "DB_HOST": database.db_instance_endpoint_address,
                "DB_NAME": "match_predictor",
                "DB_USER": MIGRATOR_USER,
            },
        )

        stack = Stack.of(self)
        db_user_arn = Arn.format(
            components=ArnComponents(
                service="rds-db",
                resource="dbuser",
                resource_name=f"{database.instance_resource_id}/{MIGRATOR_USER}",
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
            properties={"Version": alembic_versions_hash()},
        )
