from constructs import Construct
from aws_cdk import aws_s3 as s3, aws_lambda, Duration
from aws_cdk.aws_lambda_nodejs import NodejsFunction


class EtlFunctions(Construct):
    def __init__(self, scope: Construct, construct_id: str, bucket: s3.Bucket) -> None:
        super().__init__(scope, construct_id)

        scraper = NodejsFunction(self, "ScraperFunction",
            entry="packages/etl/src/lambda-handler.ts",
            handler="handler",
            runtime=aws_lambda.Runtime.NODEJS_22_X,
            project_root=".",
            deps_lock_file_path="pnpm-lock.yaml",
            timeout=Duration.minutes(5),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
            },
        )

        bucket.grant_write(scraper)
