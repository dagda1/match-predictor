# Tear down DeployStack to stop the ~$45/mo (NAT + RDS + EFS)

Everything in `DeployStack` has `RemovalPolicy.DESTROY`, so this removes it cleanly. The website (`cutting.scot`) and frontendsupport are separate stacks and are untouched.

## Destroy

```
cdk destroy DeployStack --app "python3 packages/deploy/app.py"
```

## Redeploy when you next work on MLflow/predictor

```
cdk deploy DeployStack --require-approval never --app "python3 packages/deploy/app.py"
```

Stand it up, do the work, tear it back down — you only pay for the hours it's running.

## Recover a DELETE_FAILED stack (bucket-not-empty + stuck migration resource)

The data bucket had objects and CloudFormation won't delete a non-empty bucket; the `DatabaseMigration` custom resource also failed its delete handler. Empty the buckets, then re-delete while retaining the stuck custom resource.

Account `313095418189`, region `us-west-2`.

### 1. Empty the data + log buckets

```
aws s3 rm s3://cuttingedge-matchpredictor-data-us-west-2-313095418189 --recursive
aws s3 rm s3://cuttingedge-matchpredictor-data-us-west-2-313095418189-logs --recursive
aws s3 rm s3://cuttingedge-matchpredictor-data-us-west-2-313095418189-frontend --recursive
```

### 2. Delete the stack, retaining the custom resource that won't delete

```
aws cloudformation delete-stack --region us-west-2 --stack-name DeployStack --retain-resources DatabaseMigrationE6E8D266
```

### 3. Wait for it to finish

```
aws cloudformation wait stack-delete-complete --region us-west-2 --stack-name DeployStack
```

If step 2 reports other resources still failing, add their logical IDs to `--retain-resources` (space-separated) and re-run. Retaining a custom resource leaves nothing real behind — it's just CloudFormation bookkeeping.

### If it fails again — list exactly what's still stuck

```
aws cloudformation describe-stack-events --region us-west-2 --stack-name DeployStack --query "StackEvents[?ResourceStatus=='DELETE_FAILED'].{Id:LogicalResourceId,Type:ResourceType,Reason:ResourceStatusReason}" --output table
```

Then re-run step 2 with every listed logical ID added to `--retain-resources` (space-separated), e.g.:

```
aws cloudformation delete-stack --region us-west-2 --stack-name DeployStack --retain-resources DatabaseMigrationE6E8D266 StorageBucket5CB7C8EA <other-ids>
```

### Subnets won't delete (DependencyViolation)

A subnet can't be deleted while something lives in it — leftover Lambda ENIs or EFS mount targets. Do NOT retain the subnets (that orphans the VPC + NAT gateway and you keep paying). Find what's pinning them.

Get the VPC id, then list every ENI in it with its owner:

```
+
```

```
aws ec2 describe-network-interfaces --region us-west-2 --filters Name=vpc-id,Values=vpc-08a168d94d0616192 --query "NetworkInterfaces[].{Id:NetworkInterfaceId,Desc:Description,Status:Status,Subnet:SubnetId,Type:InterfaceType}" --output table
```

Paste that table back.

### Clear leftover `available` Lambda ENIs, then finish the delete

These detach automatically ~20–40 min after the functions are gone, but you can delete them now since they're `available`. This deletes every detached ENI in the VPC:

```
for eni in $(aws ec2 describe-network-interfaces --region us-west-2 --filters Name=vpc-id,Values=vpc-08a168d94d0616192 Name=status,Values=available --query "NetworkInterfaces[].NetworkInterfaceId" --output text); do aws ec2 delete-network-interface --region us-west-2 --network-interface-id "$eni"; done
```

Then re-run the delete (no retain — the subnets can go now):

```
aws cloudformation delete-stack --region us-west-2 --stack-name DeployStack
aws cloudformation wait stack-delete-complete --region us-west-2 --stack-name DeployStack
```
