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

from deploy.deploy_stack.database_users import MLFLOW_MIGRATOR_USER
from deploy.deploy_stack.mlflow_version import REPO_DIR, mlflow_version

MLFLOW_DB_NAME = "mlflow"


class Mlflow(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        database: rds.DatabaseInstance,
        vpc: ec2.Vpc,
        security_group: ec2.SecurityGroup,
    ) -> None:
        super().__init__(scope, construct_id)

        version = mlflow_version()

        handler_function = aws_lambda.DockerImageFunction(self, "HandlerFunction",
            code=aws_lambda.DockerImageCode.from_image_asset(
                str(REPO_DIR),
                file="packages/ml/mlflow.Dockerfile",
                build_args={"MLFLOW_VERSION": version},
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
            timeout=Duration.minutes(15),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[security_group],
            ipv6_allowed_for_dual_stack=True,
            environment={
                "DB_HOST": database.db_instance_endpoint_address,
                "DB_USER": MLFLOW_MIGRATOR_USER,
                "MLFLOW_DB_NAME": MLFLOW_DB_NAME,
            },
        )

        stack = Stack.of(self)
        db_user_arn = Arn.format(
            components=ArnComponents(
                service="rds-db",
                resource="dbuser",
                resource_name=f"{database.instance_resource_id}/{MLFLOW_MIGRATOR_USER}",
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
            properties={"Version": version},
        )
