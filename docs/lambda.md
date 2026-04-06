# Lambda

## List Lambda functions

```bash
aws lambda list-functions \
  --query "Functions[?contains(FunctionName, 'Scraper')].FunctionName" \
  --output text
```

## List API Lambda

```bash
aws lambda list-functions \
  --query "Functions[?contains(FunctionName, 'Api')].FunctionName" \
  --output text
```

## Check API Lambda logs

```bash
aws logs tail \
  "/aws/lambda/DeployStack-ApiApiFunctionAA82C666-POOunoG59B74" \
  --since 1h
```

## Invoke scraper Lambda

```bash
aws lambda invoke \
  --function-name DeployStack-EtlFunctionsScraperFunctionF099BA00-y4cYA3lFkTkZ \
  --cli-read-timeout 600 \
  /tmp/scraper-output.json && cat /tmp/scraper-output.json
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

## Verify full pipeline ran

Check scraper logs:

```bash
aws logs tail \
  "/aws/lambda/DeployStack-EtlFunctionsScraperFunctionF099BA00-t23rQIlM3RwA" \
  --since 24h
```

Find predictor function name:

```bash
aws lambda list-functions \
  --query "Functions[?contains(FunctionName, 'Predictor')].FunctionName" \
  --output text
```

Check predictor logs (use name from above):

```bash
aws logs tail \
  "/aws/lambda/DeployStack-EtlFunctionsPredictorFunctionE33E3D43-CcmNKbXb8AH6" \
  --since 1h
```

Check S3 files were updated:

```bash
aws s3 ls s3://cuttingedge-matchpredictor-data-us-west-2-313095418189/predictions/
aws s3 ls s3://cuttingedge-matchpredictor-data-us-west-2-313095418189/upcoming/
```

## Check Lambda timeout

```bash
aws lambda get-function-configuration \
  --function-name DeployStack-EtlFunctionsPredictorFunctionE33E3D43-CcmNKbXb8AH6 \
  --query "Timeout" \
  --output text
```

## Check API Lambda errors (last hour)

```bash
aws logs filter-log-events \
  --log-group-name "/aws/lambda/DeployStack-ApiApiFunctionAA82C666-POOunoG59B74" \
  --filter-pattern "ERROR" \
  --start-time $(python3 -c "import time; print(int((time.time() - 3600) * 1000))")
```

## Check predictor Lambda errors (last hour)

```bash
aws logs filter-log-events \
  --log-group-name "/aws/lambda/DeployStack-EtlFunctionsPredictorFunctionE33E3D43-CcmNKbXb8AH6" \
  --filter-pattern "ERROR" \
  --start-time $(python3 -c "import time; print(int((time.time() - 3600) * 1000))")
```

## Invoke predictor manually

```bash
aws lambda invoke \
    --function-name DeployStack-EtlFunctionsPredictorFunctionE33E3D43-CcmNKbXb8AH6 \
    /tmp/predictor-output.json && cat /tmp/predictor-output.json
```
