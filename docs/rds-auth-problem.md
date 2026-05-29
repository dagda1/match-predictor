# Post-deploy orchestration

## Current state

Bootstrap and mlflow are plain Lambdas invoked from CI after `cdk deploy`. This works but leaks `lambda:InvokeFunction` into `GitHubActionRole` and breaks for deploys outside CI.

## Plan: Step Functions

Replace the CI `aws lambda invoke` steps with an in-AWS state machine triggered by CloudFormation stack-complete events.

## Checklist

- [ ] `post_deploy.py` construct: STANDARD StateMachine chaining bootstrap → mlflow (EXPRESS caps at 5 min; mlflow Lambda needs up to 15), EventBridge rule on stack-update-complete, IAM scoped to those two functions.
- [ ] Wire into `deploy_stack.py`. Drop the two `CfnOutput`s.
- [ ] Remove the two invoke steps from `deploy.yml`.
- [ ] Trigger the state machine manually once for the first deploy (the rule doesn't exist yet when its own deploy event fires).
- [ ] Tick "AWS Step Functions" in `plans/mlops.md`.
