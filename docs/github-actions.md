# GitHub Actions

## Get the GitHub Actions IAM role ARN

```bash
aws iam list-roles \
  --query "Roles[?contains(RoleName, 'GitHubAction')].Arn" \
  --output text
```

Update the `AWS_ROLE_ARN` secret in the GitHub repo settings with this value.
