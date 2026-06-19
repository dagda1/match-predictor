# MLflow backend-store bootstrap — debug

The `mlflow` Postgres DB is created + schema-migrated by a Lambda (`mlflow_bootstrap_handler.py`, wired in `deploy_stack/mlflow.py`). It connects to RDS as `mlflow_migrator` using an IAM auth token. A **PAM** error = RDS rejected that token auth.

DeployStack (and so this Lambda) lives in **us-west-2**.

## Fast iteration — hotswap instead of full deploy

Once the function exists in the stack, code/image changes to the mlflow Lambda deploy in seconds by bypassing CloudFormation:

```
cdk deploy DeployStack --hotswap-fallback --require-approval never --app "python3 packages/deploy/app.py"
```

`--hotswap-fallback` updates just the changed Lambda directly; it only falls back to a full deploy if a change can't be hotswapped. Then re-run the invoke block below.

## 1. Confirm the function is deployed and get its exact name

```
aws lambda list-functions --region us-west-2 --query "Functions[?contains(FunctionName,'lflow')].FunctionName" --output text
```

If this prints nothing, the mlflow Lambda isn't deployed — `cdk deploy DeployStack` first.

## 2. Invoke it manually and capture the result

```
aws lambda invoke --region us-west-2 --function-name $(aws lambda list-functions --region us-west-2 --query "Functions[?contains(FunctionName,'lflow')].FunctionName" --output text) /tmp/mlflow-out.json && cat /tmp/mlflow-out.json
```
## 3. Tail the mlflow Lambda logs

```
aws logs tail /aws/lambda/$(aws lambda list-functions --region us-west-2 --query "Functions[?contains(FunctionName,'lflow')].FunctionName" --output text) --region us-west-2 --since 1h --format short
```

## 4. Confirm the mlflow_migrator role exists with rds_iam (run from a psql session)

```
SELECT rolname, rolcreatedb FROM pg_roles WHERE rolname = 'mlflow_migrator';
```

```
SELECT r.rolname AS member, g.rolname AS granted FROM pg_auth_members m JOIN pg_roles r ON m.member = r.oid JOIN pg_roles g ON m.roleid = g.oid WHERE r.rolname = 'mlflow_migrator';
```

Expect `mlflow_migrator` present, `rolcreatedb = t`, and `rds_iam` in the granted list. If the role is missing, the bootstrap Lambda never ran before the mlflow Lambda — that ordering is exactly what the Step Functions chain in `post_deploy.py` fixes.
