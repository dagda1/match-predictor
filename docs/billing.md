# Billing

## Check monthly costs

```bash
aws ce get-cost-and-usage \
  --time-period Start=2026-03-01,End=2026-03-30 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --output json
```

## Current month costs by service

```bash
aws ce get-cost-and-usage \
  --time-period Start=$(date -u +%Y-%m-01),End=$(date -u +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --query "ResultsByTime[0].Groups[?Metrics.UnblendedCost.Amount!='0'].[Keys[0],Metrics.UnblendedCost.Amount]" \
  --output table
```
