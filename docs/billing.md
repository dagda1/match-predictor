# Billing

## Check monthly costs

```bash
aws ce get-cost-and-usage \
  --time-period Start=2026-03-01,End=2026-03-30 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --output json
```
