FROM public.ecr.aws/lambda/python:3.13

COPY packages/ml/pyproject.toml /tmp/ml/pyproject.toml
COPY packages/ml/src/match_predictor/ /tmp/ml/src/match_predictor/
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir boto3 /tmp/ml/

COPY packages/ml/src/match_predictor/ match_predictor/
COPY assets/rds-ca-bundle.pem rds-ca-bundle.pem

CMD ["match_predictor.lambda_handler.handler"]
