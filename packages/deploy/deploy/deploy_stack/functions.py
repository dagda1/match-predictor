from typing import List

import jsii
from constructs import Construct
from aws_cdk import (
    Arn,
    ArnComponents,
    ArnFormat,
    Duration,
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_lambda,
    aws_rds as rds,
    aws_s3 as s3,
)
from aws_cdk.aws_lambda_nodejs import (
    BundlingOptions,
    ICommandHooks,
    NodejsFunction,
    OutputFormat,
)
from pathlib import Path

from deploy.deploy_stack.database_users import APP_USER
from deploy.deploy_stack.model_storage import ModelStorage

REPO_DIR = Path(__file__).resolve().parents[4]


@jsii.implements(ICommandHooks)
class IncludeRdsCaBundle:
    def before_bundling(self, _input_dir: str, _output_dir: str) -> List[str]:
        return []

    def before_install(self, _input_dir: str, _output_dir: str) -> List[str]:
        return []

    def after_bundling(self, input_dir: str, output_dir: str) -> List[str]:
        return [
            f"cp {input_dir}/assets/rds-ca-bundle.pem {output_dir}/"
        ]


class EtlFunctions(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        bucket: s3.Bucket,
        database: rds.DatabaseInstance,
        model_storage: ModelStorage,
        vpc: ec2.Vpc,
        security_group: ec2.SecurityGroup,
    ) -> None:
        super().__init__(scope, construct_id)

        subnet_selection = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
        stack = Stack.of(self)

        db_user_arn = Arn.format(
            components=ArnComponents(
                service="rds-db",
                resource="dbuser",
                resource_name=f"{database.instance_resource_id}/{APP_USER}",
                arn_format=ArnFormat.COLON_RESOURCE_NAME,
            ),
            stack=stack,
        )

        db_environment = {
            "DB_HOST": database.db_instance_endpoint_address,
            "DB_NAME": "match_predictor",
            "DB_USER": APP_USER,
            "DB_REGION": stack.region,
        }

        self.scraper = NodejsFunction(self, "ScraperFunction",
            entry=str(REPO_DIR / "packages" / "etl" / "src" / "lambda-handler.ts"),
            project_root=str(REPO_DIR),
            deps_lock_file_path=str(REPO_DIR / "pnpm-lock.yaml"),
            handler="handler",
            runtime=aws_lambda.Runtime.NODEJS_24_X,
            timeout=Duration.minutes(5),
            tracing=aws_lambda.Tracing.ACTIVE,
            vpc=vpc,
            vpc_subnets=subnet_selection,
            security_groups=[security_group],
            ipv6_allowed_for_dual_stack=True,
            bundling=BundlingOptions(
                format=OutputFormat.ESM,
                node_modules=["pg"],
                command_hooks=IncludeRdsCaBundle(),
            ),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                **db_environment,
            },
        )

        self.predictor = aws_lambda.DockerImageFunction(self, "PredictorFunction",
            code=aws_lambda.DockerImageCode.from_image_asset(
                str(REPO_DIR),
                file="packages/ml/src/Dockerfile",
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
            memory_size=1024,
            tracing=aws_lambda.Tracing.ACTIVE,
            timeout=Duration.minutes(15),
            vpc=vpc,
            vpc_subnets=subnet_selection,
            security_groups=[security_group],
            ipv6_allowed_for_dual_stack=True,
            filesystem=model_storage.lambda_file_system(),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "MODEL_PATH": f"{ModelStorage.MOUNT_PATH}/model.joblib",
                **db_environment,
            },
        )

        self.predictor.add_to_role_policy(
            iam.PolicyStatement(
                actions=["rds-db:connect"],
                resources=[db_user_arn],
            )
        )

        self.scraper.add_to_role_policy(
            iam.PolicyStatement(
                actions=["rds-db:connect"],
                resources=[db_user_arn],
            )
        )

        bucket.grant_write(self.scraper)
        bucket.grant_read_write(self.predictor)
