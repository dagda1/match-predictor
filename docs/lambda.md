# Lambda

## List Lambda functions

```bash
aws lambda list-functions \
  --query "Functions[?contains(FunctionName, 'Scraper')].FunctionName" \
  --output text
```

## Invoke a Lambda manually

```bash
aws lambda invoke \
  --function-name <function-name> \
  /tmp/lambda-output.json && cat /tmp/lambda-output.json
```

## Check if a Lambda ran (last 24 hours)

```bash
aws logs tail "/aws/lambda/<function-name>" \
  --since 24h
```

## Check Lambda environment variables

```bash
aws lambda get-function-configuration \
  --function-name DeployStack-EtlFunctionsScraperFunctionF099BA00-t23rQIlM3RwA \
  --query "Environment.Variables" \
  --output json
```

## Check Lambda errors

```bash
aws logs filter-log-events \
  --log-group-name "/aws/lambda/<function-name>" \
  --filter-pattern "ERROR"
```
