from aws_cdk import (
    aws_s3 as s3,
    aws_kinesisfirehose as firehose,
    aws_logs as logs,
    aws_logs_destinations as logs_destinations,
    aws_lambda,
)
from aws_cdk.aws_lambda_nodejs import NodejsFunction
from constructs import Construct

class Firehose(Construct):
    def __init__(self, scope: Construct, construct_id: str, bucket: s3.Bucket, transformer: NodejsFunction) -> None:
        super().__init__(scope, construct_id)

        lambda_processor = firehose.LambdaFunctionProcessor(transformer)
        
        self.firehose = firehose.DeliveryStream(self, 
            "DeliveryStream", 
            destination=firehose.S3Bucket(
                bucket,
                data_output_prefix="logs/",
                processors=[lambda_processor]
            ),
        )


    def subscribe(self, log_group):
        logs.SubscriptionFilter(self, 
            "SubscriptionFilter", 
            log_group=log_group, 
            destination=logs_destinations.FirehoseDestination(self.firehose),
            filter_pattern=logs.FilterPattern.all_events()
        )