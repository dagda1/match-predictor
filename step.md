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

Everything deploys to **us-west-2**, so every command pins `--region us-west-2`.

## 1. Check the state machine was created

```
aws stepfunctions list-state-machines --region us-west-2
```

Lists every state machine with its `stateMachineArn` and `name`.

## 2. Get the ARN into a variable

```
SM_ARN=$(aws stepfunctions list-state-machines --region us-west-2 --query "stateMachines[?contains(name, 'PostDeploy')].stateMachineArn | [0]" --output text)
echo "$SM_ARN"
```

## 3. Manually trigger a run

```
aws stepfunctions start-execution --region us-west-2 --state-machine-arn "$SM_ARN" --input '{}'
```

## 4. Why the latest FAILED execution failed

```
SM_ARN=$(aws stepfunctions list-state-machines --region us-west-2 --query "stateMachines[?contains(name, 'PostDeploy')].stateMachineArn | [0]" --output text) \
&& EXEC_ARN=$(aws stepfunctions list-executions --region us-west-2 --state-machine-arn "$SM_ARN" --status-filter FAILED --max-results 1 --query "executions[0].executionArn" --output text) \
&& aws stepfunctions describe-execution --region us-west-2 --execution-arn "$EXEC_ARN" --query "{status:status,error:error,cause:cause}" --output json
```

The `cause` field shows which Lambda threw and the exception text.

## 5. Fix the failing architecture-diagram CI check

The email/alarm additions to `post_deploy.py` changed CDK synth output, so the committed `docs/architecture.dot` is stale and `git diff --exit-code` fails. Regenerate and commit:

```
pnpm arch:dia && git add docs/architecture.dot docs/architecture.png && git commit -m "chore: regenerate architecture diagram for PostDeploy failure alerts" && git push
```
