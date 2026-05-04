# Smoke tests

## After deploy — check `/predict` works in prod

```bash
curl -X POST https://premierpredictor.co.uk/api/predict -H "Content-Type: application/json" -d '{"homeTeamId":"Arsenal","awayTeamId":"Chelsea"}'
```

Expected outcomes:

- **200 + prediction body** — full chain works (TLS to RDS, EFS read of model, team_features populated).
- **503 model not ready** — predictor hasn't finished. Wait, retry.
- **400 insufficient data** — `team_features` empty for one of those teams. Predictor didn't populate.
- **5xx** — TLS, EFS mount, or container startup broken.

## Tail predictor logs after deploy

```bash
aws logs tail /aws/lambda/DeployStack-EtlFunctionsPredictorFunctionE33E3D43-rpZz9BeJbbiv --since 10m --follow
```

## Tail API logs

```bash
aws logs tail /aws/lambda/DeployStack-ApiApiFunctionAA82C666-POOunoG59B74 --since 10m --follow

aws logs tail /aws/lambda/DeployStack-ApiApiFunctionAA82C666-POOunoG59B74 --since 10m --filter-pattern "ERROR ?Error ?Exception ?Traceback" 2>&1 | tail -30
```
