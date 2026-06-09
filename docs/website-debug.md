# Website deploy — debug

Container now pulls and runs, then exits (`EssentialContainerExited`). Need its logs.

## Step 1 — find the current log group

```
aws logs describe-log-groups \
  --region us-east-1 \
  --query "logGroups[?contains(logGroupName, 'Website')].logGroupName" \
  --output text
```

## Step 2 — tail it (paste the name from step 1)

```
aws logs tail <log-group-name> --region us-east-1 --since 1h --format short
```

---

## Redeploy from scratch (when needed)

```
aws cloudformation delete-stack --region us-east-1 --stack-name WebsiteStack
aws cloudformation wait stack-delete-complete --region us-east-1 --stack-name WebsiteStack
cd packages/deploy && cdk deploy WebsiteStack --no-rollback --require-approval never
```

## Tail the newest log group (one line)

```
NEWEST=$(aws logs describe-log-groups --region us-east-1 --query "reverse(sort_by(logGroups[?contains(logGroupName,'Website')],&creationTime))[0].logGroupName" --output text); aws logs tail "$NEWEST" --region us-east-1 --since 1h --format short
```