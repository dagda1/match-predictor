FROM public.ecr.aws/lambda/python:3.12

COPY packages/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY packages/ml/src/match_predictor/ match_predictor/
COPY packages/api/src/match_predictor_api/ match_predictor_api/

CMD ["match_predictor_api.lambda_handler.handler"]
