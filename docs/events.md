# EventBridge

## List all rules

```bash
aws events list-rules --output json
```

## List rules matching a name

```bash
aws events list-rules \
  --query "Rules[?contains(Name, 'Scraper')]" \
  --output json
```

## Check rule details

```bash
aws events describe-rule \
  --name DeployStack-EventBridgeDailyScraperRule9BFD8304-QiQDbaX1ks3d
```

## List targets for a rule

```bash
aws events list-targets-by-rule \
  --rule DeployStack-EventBridgeDailyScraperRule9BFD8304-QiQDbaX1ks3d
```

## Check if a rule has fired (invocation count)

```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Events \
  --metric-name Invocations \
  --dimensions Name=RuleName,Value=DeployStack-EventBridgeDailyScraperRule9BFD8304-QiQDbaX1ks3d \
  --start-time 2026-03-25T00:00:00Z \
  --end-time 2026-03-26T23:59:59Z \
  --period 86400 \
  --statistics Sum
```
