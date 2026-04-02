# CloudFront

## Check if distribution was created

```bash
aws cloudfront list-distributions \
  --query "DistributionList.Items[].{Id:Id,Domain:DomainName,Status:Status,Comment:Comment,LastModified:LastModifiedTime}" \
  --output table
```

## Get distribution ID from stack outputs

```bash
aws cloudformation describe-stacks \
  --stack-name DeployStack \
  --query "Stacks[0].Outputs[?OutputKey=='DistributionId'].OutputValue" \
  --output text
```

## Get distribution domain name

```bash
aws cloudformation describe-stacks \
  --stack-name DeployStack \
  --query "Stacks[0].Outputs[?OutputKey=='DistributionDomain'].OutputValue" \
  --output text
```

## Invalidate index.html after deploy

```bash
aws cloudfront create-invalidation \
  --distribution-id <distribution-id> \
  --paths "/index.html"
```
