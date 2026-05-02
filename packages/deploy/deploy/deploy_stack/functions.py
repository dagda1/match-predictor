from constructs import Construct
from aws_cdk import (
    aws_s3 as s3,
    aws_lambda,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_rds as rds,
    Duration,
    Stack,
)
from aws_cdk.aws_lambda_nodejs import NodejsFunction
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[4]

APP_USER = "match_predictor_app"


class EtlFunctions(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        bucket: s3.Bucket,
        database: rds.DatabaseInstance,
        vpc: ec2.Vpc,
        security_group: ec2.SecurityGroup,
    ) -> None:
        super().__init__(scope, construct_id)

        subnet_selection = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
        stack = Stack.of(self)

        db_user_arn = (
            f"arn:aws:rds-db:{stack.region}:{stack.account}"
            f":dbuser:{database.instance_resource_id}/{APP_USER}"
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
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                **db_environment,
            },
        )

        self.predictor = aws_lambda.DockerImageFunction(self, "PredictorFunction",
            code=aws_lambda.DockerImageCode.from_image_asset(
                str(REPO_DIR / "packages" / "ml"),
                file="src/Dockerfile",
                exclude=["__pycache__", ".venv"],
            ),
            memory_size=1024,
            tracing=aws_lambda.Tracing.ACTIVE,
            timeout=Duration.minutes(15),
            vpc=vpc,
            vpc_subnets=subnet_selection,
            security_groups=[security_group],
            ipv6_allowed_for_dual_stack=True,
            environment={
                "BUCKET_NAME": bucket.bucket_name,
            },
        )

        self.scraper.add_to_role_policy(
            iam.PolicyStatement(
                actions=["rds-db:connect"],
                resources=[db_user_arn],
            )
        )

        bucket.grant_write(self.scraper)
        bucket.grant_read_write(self.predictor)
