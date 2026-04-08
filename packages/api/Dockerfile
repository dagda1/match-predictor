FROM public.ecr.aws/lambda/python:3.12

COPY packages/ml/pyproject.toml /tmp/ml/pyproject.toml
COPY packages/ml/src/match_predictor/ /tmp/ml/src/match_predictor/
RUN pip install --no-cache-dir /tmp/ml/

COPY packages/api/pyproject.toml /tmp/api/pyproject.toml
COPY packages/api/src/match_predictor_api/ /tmp/api/src/match_predictor_api/
RUN pip install --no-cache-dir mangum boto3 /tmp/api/

COPY packages/ml/src/match_predictor/ match_predictor/
COPY packages/api/src/match_predictor_api/ match_predictor_api/

CMD ["match_predictor_api.lambda_handler.handler"]
