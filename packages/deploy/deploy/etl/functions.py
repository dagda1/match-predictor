import os

from constructs import Construct
from aws_cdk import aws_s3 as s3, aws_lambda, aws_sns, aws_sns_subscriptions, Duration
from aws_cdk.aws_lambda_nodejs import NodejsFunction


class EtlFunctions(Construct):
    def __init__(self, scope: Construct, construct_id: str, bucket: s3.Bucket) -> None:
        super().__init__(scope, construct_id)

        self.topic = aws_sns.Topic(self, "ScraperAlerts")
        self.topic.add_subscription(
            aws_sns_subscriptions.EmailSubscription(os.environ["AWS_ALARM_EMAIL"])
        )

        self.scraper = NodejsFunction(self, "ScraperFunction",
            entry="packages/etl/src/lambda-handler.ts",
            handler="handler",
            runtime=aws_lambda.Runtime.NODEJS_24_X,
            project_root=".",
            deps_lock_file_path="pnpm-lock.yaml",
            timeout=Duration.minutes(5),
            tracing=aws_lambda.Tracing.ACTIVE,
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "TOPIC_ARN": self.topic.topic_arn,
            },
        )

        bucket.grant_write(self.scraper)
        self.topic.grant_publish(self.scraper)
