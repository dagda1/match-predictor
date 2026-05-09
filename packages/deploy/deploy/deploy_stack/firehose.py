from aws_cdk import (
    aws_s3 as s3,
    aws_kinesisfirehose as firehose,
    aws_logs as logs,
    aws_logs_destinations as logs_destinations,
)
from constructs import Construct

class Firehose(Construct):
    def __init__(self, scope: Construct, construct_id: str, bucket: s3.Bucket) -> None:
        super().__init__(scope, construct_id)

        self.firehose = firehose.DeliveryStream(self, "DeliveryStream", destination=firehose.S3Bucket(bucket, data_output_prefix="logs/"))

    def subscribe(self, log_group):
        log_filter = logs.SubscriptionFilter(self, 
            "SubscriptionFilter", 
            log_group=log_group, 
            destination=logs_destinations.FirehoseDestination(self.firehose),
            filter_pattern=logs.FilterPattern.all_events()
        )