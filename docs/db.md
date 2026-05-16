# Database operations

## Inspect the master credentials stored in Secrets Manager

Pulls only the username and dbname fields — no password material is printed.

```bash
aws secretsmanager get-secret-value \
  --secret-id $(aws cloudformation describe-stack-resources \
    --stack-name DeployStack \
    --query "StackResources[?LogicalResourceId=='DatabasePostgresSecret6EBE3413'].PhysicalResourceId" \
    --output text) \
  --query SecretString --output text | jq '{username, dbname}'
```

Use when the bootstrap Lambda fails with `password authentication failed` or `PAM authentication failed for user "postgres"` — the error message contains the username Lambda actually sent, which must match the `username` field returned here.
