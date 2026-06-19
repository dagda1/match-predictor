# Actual AWS cost, month-to-date, by service

Run this. It returns the real unblended cost per service for the current month — no estimates.

```
aws ce get-cost-and-usage \
  --time-period Start=2026-06-01,End=2026-06-30 \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --query "ResultsByTime[0].Groups[?Metrics.UnblendedCost.Amount!='0'].{Service:Keys[0],USD:Metrics.UnblendedCost.Amount}" \
  --output table
```

Cost Explorer is global — region doesn't matter.

Paste the table back and I'll tell you which line items to kill.
