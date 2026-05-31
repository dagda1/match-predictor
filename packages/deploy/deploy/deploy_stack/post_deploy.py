import os

from aws_cdk import (
    Duration,
    Stack,
    aws_cloudwatch_actions,
    aws_events,
    aws_events_targets,
    aws_lambda,
    aws_sns,
    aws_sns_subscriptions,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
)
from constructs import Construct


class PostDeploy(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        bootstrap_function: aws_lambda.IFunction,
        mlflow_function: aws_lambda.IFunction,
    ) -> None:
        super().__init__(scope, construct_id)

        bootstrap_task = tasks.LambdaInvoke(self, "BootstrapTask",
            lambda_function=bootstrap_function,
            payload=sfn.TaskInput.from_object({}),
        )

        mlflow_task = tasks.LambdaInvoke(self, "MlflowTask",
            lambda_function=mlflow_function,
            payload=sfn.TaskInput.from_object({}),
        )

        self.state_machine = sfn.StateMachine(self, "StateMachine",
            definition_body=sfn.DefinitionBody.from_chainable(
                bootstrap_task.next(mlflow_task)
            ),
            state_machine_type=sfn.StateMachineType.STANDARD,
            timeout=Duration.minutes(20),
        )

        rule = aws_events.Rule(self, "StackCompleteRule",
            description="Runs post-deploy bootstrap when DeployStack finishes",
            event_pattern=aws_events.EventPattern(
                source=["aws.cloudformation"],
                detail_type=["CloudFormation Stack Status Change"],
                detail={
                    "stack-id": [Stack.of(self).stack_id],
                    "status-details": {
                        "status": ["CREATE_COMPLETE", "UPDATE_COMPLETE"],
                    },
                },
            ),
        )

        rule.add_target(aws_events_targets.SfnStateMachine(self.state_machine))

        topic = aws_sns.Topic(self, "FailureAlerts")
        topic.add_subscription(
            aws_sns_subscriptions.EmailSubscription(os.environ["AWS_ALARM_EMAIL"])
        )

        failure_alarm = self.state_machine.metric_failed().create_alarm(self, "ExecutionFailedAlarm",
            threshold=1,
            evaluation_periods=1,
        )
        failure_alarm.add_alarm_action(aws_cloudwatch_actions.SnsAction(topic))
