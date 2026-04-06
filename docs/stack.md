## return all logical IDs for all failed resources

```bash
aws cloudformation describe-stack-events \
    --stack-name CertificateStack \
    --region us-east-1 \
    --query "StackEvents[?ResourceStatus=='UPDATE_FAILED'].LogicalResourceId" \
    --output text
```

## Skip a failed resource during rollback

Use when a resource was deleted outside CloudFormation and the stack is stuck in `UPDATE_ROLLBACK_FAILED`.

```bash
aws cloudformation continue-update-rollback \
  --stack-name DeployStack \
  --resources-to-skip <LogicalResourceId>
```

e.g.

```bash
aws cloudformation continue-update-rollback \
  --stack-name CertificateStack \
  --region us-east-1 \
  --resources-to-skip ExportsWriteruswest209BD44F0A7CF058B
```

## Check stack status

```bash
aws cloudformation describe-stacks \
  --stack-name CertificateStack \
  --region us-east-1 \
  --query "Stacks[0].StackStatus" \
  --output text
```