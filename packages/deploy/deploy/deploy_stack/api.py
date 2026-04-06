from constructs import Construct
from aws_cdk import aws_lambda, aws_apigatewayv2 as apigw, aws_s3 as s3, aws_secretsmanager as secretsmanager, Duration
from aws_cdk.aws_apigatewayv2_integrations import HttpLambdaIntegration
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[4]


class Api(Construct):
    def __init__(self, scope: Construct, construct_id: str, bucket: s3.Bucket, origin_verify_secret: secretsmanager.Secret) -> None:
        super().__init__(scope, construct_id)

        self.function = aws_lambda.DockerImageFunction(self, "ApiFunction",
            code=aws_lambda.DockerImageCode.from_image_asset(
                str(REPO_DIR),
                file="packages/api/Dockerfile",
                exclude=["node_modules", "packages/deploy/cdk.out", ".git", "dist", ".venv", "__pycache__", ".turbo"],
            ),
            timeout=Duration.seconds(30),
            memory_size=1024,
            tracing=aws_lambda.Tracing.ACTIVE,
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "ORIGIN_SECRET_ARN": origin_verify_secret.secret_arn,
            },
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
