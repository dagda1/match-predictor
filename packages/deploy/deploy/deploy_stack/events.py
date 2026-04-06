from aws_cdk.aws_lambda_nodejs import NodejsFunction
from constructs import Construct
from aws_cdk import aws_events, aws_events_targets

class Events(Construct):
    def __init__(self, scope: Construct, construct_id: str, scraper_function: NodejsFunction) -> None:
        super().__init__(scope, construct_id)

        rule = aws_events.Rule(self, "DailyScraperRule",
            schedule=aws_events.Schedule.cron(hour="6", minute="0"),
            description="Triggers scraper Lambda daily at 06:00 UTC",
        )

        rule.add_target(aws_events_targets.LambdaFunction(scraper_function))