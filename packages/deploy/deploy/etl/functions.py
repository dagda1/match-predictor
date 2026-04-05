from constructs import Construct
from aws_cdk import aws_s3 as s3, aws_lambda, Duration
from aws_cdk.aws_lambda_nodejs import NodejsFunction
from pathlib import Path

DEPLOY_DIR = Path(__file__).resolve().parent.parent.parent
REPO_DIR = DEPLOY_DIR.parent.parent

class EtlFunctions(Construct):
    def __init__(self, scope: Construct, construct_id: str, bucket: s3.Bucket) -> None:
        super().__init__(scope, construct_id)

        self.scraper = NodejsFunction(self, "ScraperFunction",
            entry=str(REPO_DIR / "packages" / "etl" / "src" / "lambda-handler.ts"),
            project_root=str(REPO_DIR),
            deps_lock_file_path=str(REPO_DIR / "pnpm-lock.yaml"),
            handler="handler",
            runtime=aws_lambda.Runtime.NODEJS_24_X,
            timeout=Duration.minutes(5),
            tracing=aws_lambda.Tracing.ACTIVE,
            environment={
                "BUCKET_NAME": bucket.bucket_name,
            },
        )

        self.predictor = aws_lambda.DockerImageFunction(self, "PredictorFunction",
            code=aws_lambda.DockerImageCode.from_image_asset(
                str(REPO_DIR / "packages" / "ml" / "src"),
                exclude=["__pycache__", ".venv"],
            ),
            memory_size=1024,
            tracing=aws_lambda.Tracing.ACTIVE,
            timeout=Duration.minutes(15),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
            },
        )

        bucket.grant_write(self.scraper)
        bucket.grant_read_write(self.predictor)
