# CloudFormation stack ops

## Check status

```bash
aws cloudformation describe-stacks \
  --stack-name DeployStack \
  --region us-west-2 \
  --query "Stacks[0].StackStatus" \
  --output text
```

## Recover from UPDATE_ROLLBACK_FAILED

1. List the resources that failed (skip the stack-level row):

   ```bash
   aws cloudformation describe-stack-events \
     --stack-name DeployStack --region us-west-2 \
     --query "StackEvents[?ResourceStatus=='UPDATE_FAILED'].LogicalResourceId" \
     --output text | tr '\t' '\n' | sort -u | grep -v '^DeployStack$'
   ```

2. Continue the rollback, skipping those resources (space-separated):

   ```bash
aws cloudformation continue-update-rollback \
  --stack-name DeployStack --region us-west-2 \
  --resources-to-skip <id1> <id2>
   ```

3. Re-check status. When it reads `UPDATE_ROLLBACK_COMPLETE`, re-deploy.

aws cloudformation continue-update-rollback \
  --stack-name DeployStack --region us-west-2 \
  --resources-to-skip ApiApiFunctionAA82C666 DatabaseBootstrapC5F0F99D EtlFunctionsPredictorFunctionE33E3D43
