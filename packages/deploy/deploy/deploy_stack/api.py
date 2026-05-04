from constructs import Construct
from aws_cdk import (
    Arn,
    ArnComponents,
    ArnFormat,
    Duration,
    Stack,
    aws_apigatewayv2 as apigw,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_lambda,
    aws_rds as rds,
    aws_s3 as s3,
    aws_secretsmanager as secretsmanager,
)
from aws_cdk.aws_apigatewayv2_integrations import HttpLambdaIntegration
from pathlib import Path

from deploy.deploy_stack.database_users import APP_USER
from deploy.deploy_stack.model_storage import ModelStorage

REPO_DIR = Path(__file__).resolve().parents[4]


class Api(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        bucket: s3.Bucket,
        origin_verify_secret: secretsmanager.Secret,
        model_storage: ModelStorage,
        database: rds.DatabaseInstance,
        vpc: ec2.Vpc,
        security_group: ec2.SecurityGroup,
    ) -> None:
        super().__init__(scope, construct_id)

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

        self.function = aws_lambda.DockerImageFunction(self, "ApiFunction",
            code=aws_lambda.DockerImageCode.from_image_asset(
                str(REPO_DIR),
                file="packages/api/Dockerfile",
                exclude=["node_modules", "**/cdk.out", ".git", "dist", ".venv", "__pycache__", ".turbo"],
            ),
            timeout=Duration.seconds(30),
            memory_size=1024,
            tracing=aws_lambda.Tracing.ACTIVE,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[security_group],
            ipv6_allowed_for_dual_stack=True,
            filesystem=model_storage.lambda_file_system(),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "ORIGIN_SECRET_ARN": origin_verify_secret.secret_arn,
                "MODEL_PATH": f"{ModelStorage.MOUNT_PATH}/model.joblib",
                "DB_HOST": database.db_instance_endpoint_address,
                "DB_NAME": "match_predictor",
                "DB_USER": APP_USER,
                "DB_REGION": stack.region,
            },
        )

        self.function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["rds-db:connect"],
                resources=[db_user_arn],
            )
        )

        bucket.grant_read(self.function)
        origin_verify_secret.grant_read(self.function)

        integration = HttpLambdaIntegration("ApiIntegration", self.function)

        self.http_api = apigw.HttpApi(self, "HttpApi")
        self.http_api.add_routes(
            path="/{proxy+}",
            methods=[apigw.HttpMethod.ANY],
            integration=integration,
        )
