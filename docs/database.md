# Database

## Check RDS instance status

```bash
aws rds describe-db-instances \
  --query "DBInstances[].{Id:DBInstanceIdentifier,Status:DBInstanceStatus,Engine:Engine,Endpoint:Endpoint.Address,Port:Endpoint.Port}" \
  --output table
```

## Check bootstrap resources deployed

```bash
aws cloudformation describe-stack-resources \
  --stack-name DeployStack \
  --query "StackResources[?contains(LogicalResourceId, 'Bootstrap')].[LogicalResourceId,ResourceStatus,PhysicalResourceId]" \
  --output table
```

## Tail bootstrap Lambda logs

```bash
aws logs tail "/aws/lambda/DeployStack-DatabaseBootstrapHandlerFunction53F127-6d7FnL3CRGae" --since 24h
```
