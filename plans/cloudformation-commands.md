# CloudFormation commands

## Check stack status

```bash
aws cloudformation describe-stacks \
  --stack-name DeployStack \
  --query "Stacks[0].StackStatus" \
  --output text
```

## List all stacks

```bash
aws cloudformation list-stacks \
  --query "StackSummaries[?StackStatus!='DELETE_COMPLETE'].StackName" \
  --output table
```

## List S3 bucket resources in the stack

```bash
aws cloudformation describe-stack-resources \
  --stack-name DeployStack \
  --output json
```

## Skip a failed resource during rollback

Use when a resource was deleted outside CloudFormation and the stack is stuck in `UPDATE_ROLLBACK_FAILED`.

```bash
aws cloudformation continue-update-rollback \
  --stack-name DeployStack \
  --resources-to-skip <LogicalResourceId>
```

## Delete an S3 bucket (empties it first)

```bash
aws s3 rb s3://<bucket-name> --force
```

## Deploy from repo root

```bash
cdk deploy --app "packages/deploy/.venv/bin/python3 packages/deploy/app.py"
```

## Synth from repo root

```bash
cdk synth --app "packages/deploy/.venv/bin/python3 packages/deploy/app.py"
```
