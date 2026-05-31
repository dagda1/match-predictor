# Post-deploy Step Functions — manual commands

Run these yourself from a terminal. (Claude is banned from running `aws`.)

## 0. Authenticate gh (one time)

`gh` is installed but returns `401 Bad credentials` until you log in:

```
gh auth login
```

If you still get `401 Bad credentials` after logging in, a stale token env var is overriding the login. Unset it:

```
unset GH_TOKEN GITHUB_TOKEN
```

## 1. Check the state machine was created

```
aws cloudformation describe-stack-resources --stack-name DeployStack --query "StackResources[?ResourceType=='AWS::StepFunctions::StateMachine'].PhysicalResourceId" --output text
```

Prints the state machine ARN if it exists, empty if not.

## 2. Get the ARN into a variable

```
SM_ARN=$(aws cloudformation describe-stack-resources --stack-name DeployStack --query "StackResources[?ResourceType=='AWS::StepFunctions::StateMachine'].PhysicalResourceId" --output text)
echo "$SM_ARN"
```

## 3. First-run manual trigger

The EventBridge rule can't catch the deploy event that created it, so the very first run is manual:

```
aws stepfunctions start-execution --state-machine-arn "$SM_ARN" --input '{}'
```

## 4. Watch the execution result

```
EXEC_ARN=$(aws stepfunctions list-executions --state-machine-arn "$SM_ARN" --max-results 1 --query "executions[0].executionArn" --output text)
aws stepfunctions describe-execution --execution-arn "$EXEC_ARN" --query "{status:status,error:error,cause:cause}" --output table
```

`status` should be `SUCCEEDED`.
