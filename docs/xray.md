# X-Ray

## List recent traces

```bash
aws xray get-trace-summaries \
  --start-time 2026-03-28T06:00:00Z \
  --end-time 2026-03-28T07:00:00Z
```

## Get full trace details

```bash
aws xray batch-get-traces \
  --trace-ids "1-69c76e6b-4a28b7896fab8046371d521e"
```

## Get trace ID from Lambda logs

The trace ID is logged with each invocation:

```bash
aws logs tail \
  "/aws/lambda/DeployStack-EtlFunctionsScraperFunctionF099BA00-t23rQIlM3RwA" \
  --since 24h \
  --filter-pattern "XRAY TraceId"
```
