from constructs import Construct
from aws_cdk import aws_sqs, aws_lambda, Duration
from aws_cdk.aws_lambda_event_sources import SqsEventSource


class Queuing(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        scraper: aws_lambda.IFunction,
        predictor: aws_lambda.IFunction,
    ) -> None:
        super().__init__(scope, construct_id)

        self.queue = aws_sqs.Queue(self, "ScraperToPredictor",
            visibility_timeout=Duration.minutes(16),
        )

        self.queue.grant_send_messages(scraper)
        scraper.add_environment("QUEUE_URL", self.queue.queue_url)
        predictor.add_event_source(SqsEventSource(self.queue))
