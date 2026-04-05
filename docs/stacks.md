# CDK Stacks

## Stacks in this project

| Stack | Region | Purpose |
|-------|--------|---------|
| CertificateStack | us-east-1 | ACM certificate for CloudFront (must be in us-east-1) |
| DeployStack | us-west-2 | Everything else — S3, Lambdas, EventBridge, CloudFront, etc. |

## Bootstrap a region

CDK needs a one-time bootstrap per region per account. This creates an S3 bucket and IAM roles that CDK uses to deploy.

```bash
cdk bootstrap aws://313095418189/us-east-1
cdk bootstrap aws://313095418189/us-west-2
```

## Deploy all stacks

```bash
cdk deploy --all --require-approval never \
  --app "packages/deploy/.venv/bin/python3 packages/deploy/app.py"
```

## Deploy a single stack

```bash
cdk deploy CertificateStack \
  --app "packages/deploy/.venv/bin/python3 packages/deploy/app.py"
```

## Destroy a stack

```bash
cdk destroy DeployStack \
  --app "packages/deploy/.venv/bin/python3 packages/deploy/app.py"
```
