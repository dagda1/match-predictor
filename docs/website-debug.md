# Website deploy — debug

Log group is `/ecs/website` (set explicitly in `ecs.py`). Tail it directly.

## Tail the logs

```
aws logs tail /ecs/website --region us-east-1 --since 1h --format short
```

## If that says the group doesn't exist — find the stopped task reason

```
TASK=$(aws ecs list-tasks --cluster website --region us-east-1 --desired-status STOPPED --query 'taskArns[0]' --output text); aws ecs describe-tasks --cluster website --region us-east-1 --tasks "$TASK" --query 'tasks[0].{stopCode:stopCode,stoppedReason:stoppedReason,containers:containers[].{name:name,reason:reason,exitCode:exitCode}}' --output json
```

---

## Delete orphaned log groups

Leftovers from the failed deploys, auto-named `WebsiteStack-EcsTaskDefWebLogGroup...`. Live logs are in `/ecs/website`, so anything under `WebsiteStack-` is safe to delete.

List them:

```
aws logs describe-log-groups --region us-east-1 --query "logGroups[?starts_with(logGroupName, 'WebsiteStack-')].logGroupName" --output text
```

Delete all of them in one go:

```
for lg in $(aws logs describe-log-groups --region us-east-1 --query "logGroups[?starts_with(logGroupName, 'WebsiteStack-')].logGroupName" --output text); do aws logs delete-log-group --region us-east-1 --log-group-name "$lg"; done
```

---

## Redeploy from scratch (when needed)

```
aws cloudformation delete-stack --region us-east-1 --stack-name WebsiteStack
aws cloudformation wait stack-delete-complete --region us-east-1 --stack-name WebsiteStack
cd packages/deploy && cdk deploy WebsiteStack --no-rollback --require-approval never
```
