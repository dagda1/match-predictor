# Website deploy — diagnose NotStabilized

Stack rolled back, but the CloudWatch log group survives. Find it, then tail it.

## 1. Find the log group

```
aws logs describe-log-groups \
  --region us-east-1 \
  --query "logGroups[?contains(logGroupName, 'Website')].logGroupName" \
  --output text
```

## 2. Tail the container output

```
aws logs tail WebsiteStack-EcsTaskDefWebLogGroupDC2E1B4B-6bzeQcw4Erpr \
  --region us-east-1 \
  --since 72h \
  --format short
```

That prints the container's stdout/stderr — a stack trace or "missing env" means it crashed on boot; clean startup logs mean it's a health-check problem instead.

## 3. No logs = container never started — catch the reason live

The task is failing before it runs (image pull / execution role / network). Once the
stack rolls back, the cluster and its tasks are deleted, so capture the reason **during**
the deploy. The circuit breaker gives a few-minute window.

**Terminal A** — start the deploy:

```
cd packages/deploy
cdk deploy WebsiteStack --require-approval never
```

**Terminal B** — once Terminal A reaches the `AWS::ECS::Service` step, run:

```
CLUSTER=$(aws ecs list-clusters --region us-east-1 \
  --query "clusterArns[?contains(@, 'WebsiteStack')]" --output text)

TASK=$(aws ecs list-tasks --region us-east-1 --cluster "$CLUSTER" \
  --desired-status STOPPED --query "taskArns[0]" --output text)

aws ecs describe-tasks --region us-east-1 --cluster "$CLUSTER" --tasks "$TASK" \
  --query "tasks[0].{stopCode:stopCode,reason:stoppedReason,containers:containers[].reason}"
```

The `containers[].reason` line is the one that matters — e.g. `CannotPullContainerError`.
