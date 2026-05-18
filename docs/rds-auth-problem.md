# RDS auth: how we got here, what to fix

## The standard pattern (what we want)

1. RDS instance created with `iam_authentication=True` and a `database_name`.
2. CDK puts the master user's password in Secrets Manager automatically.
3. The bootstrap Lambda reads the secret and connects as `postgres` with `password=<from secret>`.
4. Bootstrap creates the application roles (`match_predictor_migrator`, `match_predictor_app`, `mlflow_migrator`) and grants `rds_iam` to those roles only.
5. App Lambdas (api, predictor, mlflow) connect using short-lived IAM tokens as their respective non-master roles.
6. The master `postgres` user keeps password-only auth and is only ever used by bootstrap.

## What actually happened on this stack

1. First deploy worked. Bootstrap ran fine with password auth.
2. At some point, `rds_iam` got granted to `postgres`. We do not know what did it — never traced via CloudTrail. Suspected: a manual SQL session, or a CDK / parameter-group change that AWS auto-applies the grant for.
3. Once `postgres` has `rds_iam`, RDS forces it through PAM/IAM-token auth only. The secret's password becomes invalid because the role no longer accepts passwords.
4. Next bootstrap run fails with `PAM authentication failed for user "postgres"`.
5. To get past it, the bootstrap Lambda was changed to use IAM token auth as `postgres`, and given `rds-db:connect` IAM permission. This worked around the symptom but cemented the broken state.
6. CustomResource lifecycle then made things worse: when a deploy fails CloudFormation rolls back, the bootstrap CustomResource often fails to roll back too, leaving the stack stuck in `UPDATE_ROLLBACK_FAILED`.
7. To break the cycle, bootstrap was converted from a CustomResource to a plain Lambda invoked by CI after `cdk deploy`. That part is genuinely better and should stay.

## Why this is wrong

- We are using IAM auth for the master user, which is non-standard. Master users normally use only the Secrets Manager password.
- We do not know what granted `rds_iam` to `postgres`. Until we find out and revoke it, we cannot return to the standard pattern.
- Every bootstrap change drags the `rds_iam` workaround along with it.

## Checklist to return to standard

- [ ] Investigate `CloudTrail` for `RebootDBInstance`, `ModifyDBInstance`, `AddRoleToDBInstance`, and any SQL session events that might have granted `rds_iam` to `postgres`.
- [ ] Connect to RDS as a role that still has password auth and run:
      `SELECT r.rolname FROM pg_auth_members m JOIN pg_roles r ON r.oid = m.roleid JOIN pg_roles u ON u.oid = m.member WHERE u.rolname = 'postgres';`
      to confirm `rds_iam` is in the membership.
- [ ] Run `REVOKE rds_iam FROM postgres;` once, as a non-master role with sufficient privilege (or via the RDS-IAM-enabled `match_predictor_migrator` which is a superuser-equivalent if it has been granted membership).
- [ ] Revert `packages/db-bootstrap/handler.py` to read the password from Secrets Manager (the original handler we replaced).
- [ ] Revert `packages/deploy/deploy/deploy_stack/bootstrap.py` to grant `secret.grant_read(handler_function)` instead of `rds-db:connect` on the master.
- [ ] Keep bootstrap as a plain Lambda invoked from CI (do not put it back inside a CustomResource).
- [ ] Re-deploy. Bootstrap should connect with password and succeed.
- [ ] Add a `REVOKE rds_iam FROM postgres;` line at the top of `bootstrap.sql` so the bad state cannot silently return.

 aws cloudtrail lookup-events \
    --region us-west-2 \
    --lookup-attributes AttributeKey=ResourceName,AttributeValue=deploystack-databasepostgres277ef4cb-4dluuy7sxwju \
    --max-results 50 \
    --query "Events[].{Time:EventTime,User:Username,Event:EventName}" \
    --output table