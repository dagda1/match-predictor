from aws_cdk import (
    aws_s3 as s3,
    aws_iam as iam,
    aws_kinesisfirehose as firehose,
)
from constructs import Construct

class Firehose(Construct):
    def __init__(self, scope: Construct, construct_id: str, bucket: s3.Bucket) -> None:
        super().__init__(scope, construct_id)
        
        role = iam.Role(self, "FirehoseRole", assumed_by=iam.ServicePrincipal("firehose.amazonaws.com"))
        bucket.grant_write(role)

        s3_destination = firehose.CfnDeliveryStream.S3DestinationConfigurationProperty(
            bucket_arn=bucket.bucket_arn,
            role_arn=role.role_arn,
            prefix="logs/",
            buffering_hints=firehose.CfnDeliveryStream.BufferingHintsProperty(
                size_in_m_bs=50,
                interval_in_seconds=300
            ),
            compression_format="GZIP"
        )

        self.firehose = firehose.CfnDeliveryStream(
            self, "FirehoseDeliveryStream",
            s3_destination_configuration=s3_destination
        )