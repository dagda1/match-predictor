from aws_cdk.aws_lambda_nodejs import NodejsFunction
from aws_cdk import aws_sns, aws_sns_subscriptions, aws_cloudwatch_actions
from constructs import Construct
import os

email = os.environ["AWS_ALARM_EMAIL"]

class Alerts(Construct):
    def __init__(self, scope: Construct, construct_id: str, scraper_function: NodejsFunction) -> None:
        super().__init__(scope, construct_id)

        topic = aws_sns.Topic(self, "ScraperAlerts")
        topic.add_subscription(aws_sns_subscriptions.EmailSubscription(email))

        alarm = scraper_function.metric_errors().create_alarm(self,
        "ScraperErrorAlarm",
            threshold=1,
            evaluation_periods=1,
        )

        alarm.add_alarm_action(aws_cloudwatch_actions.SnsAction(topic))