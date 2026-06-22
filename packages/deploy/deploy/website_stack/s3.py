from aws_cdk import (
    CfnOutput,
    RemovalPolicy,
    Stack,
    aws_s3 as s3,
)
from constructs import Construct


class Storage(Construct):
    def __init__(self, scope: Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)

        self.bucket = s3.Bucket(self, "SiteBucket",
            bucket_name=f"cutting-scot-site-{Stack.of(self).account}",
            website_index_document="index.html",
            website_error_document="index.html",
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
            ),
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        CfnOutput(scope, "WebsiteSiteBucket", value=self.bucket.bucket_name)
