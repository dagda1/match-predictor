FROM public.ecr.aws/lambda/python:3.12

COPY pyproject.toml /tmp/ml/pyproject.toml
COPY src/match_predictor/ /tmp/ml/src/match_predictor/
RUN pip install --no-cache-dir boto3 /tmp/ml/

COPY src/match_predictor/ match_predictor/

CMD ["match_predictor.lambda_handler.handler"]
