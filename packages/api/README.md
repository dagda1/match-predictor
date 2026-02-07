# Match Predictor API

FastAPI server for football match predictions using Monte Carlo simulation.

## Setup

```bash
cd packages/api
uv sync
```

## Start

```bash
cd packages/api
uv run uvicorn match_predictor_api.main:app --port 4400 --reload
```

API available at http://localhost:4400

Swagger docs at http://localhost:4400/docs

## Stop

`Ctrl+C` in the terminal running the server.

## Query

### List teams

```bash
curl http://localhost:4400/teams
```

### Predict a match

```bash
curl -X POST http://localhost:4400/predict \
  -H 'Content-Type: application/json' \
  -d '{"homeTeamId": "Liverpool", "awayTeamId": "Manchester City"}'
```

Response:

```json
{
  "homeWin": 0.51,
  "draw": 0.23,
  "awayWin": 0.26,
  "scorelines": [
    { "homeGoals": 1, "awayGoals": 1, "probability": 0.105 },
    { "homeGoals": 2, "awayGoals": 1, "probability": 0.089 }
  ]
}
```
