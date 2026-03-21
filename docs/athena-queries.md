# Athena queries

## Run a query

```bash
aws athena start-query-execution \
  --query-string "SELECT * FROM match_predictor.matches LIMIT 5" \
  --result-configuration "OutputLocation=s3://cuttingedge-matchpredictor-data-us-west-2-313095418189/athena-results/"
```

Returns a `QueryExecutionId`.

## Get query results

```bash
aws athena get-query-results \
  --query-execution-id <query-execution-id>
```

