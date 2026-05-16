FROM public.ecr.aws/lambda/python:3.13

  ARG MLFLOW_VERSION
  RUN pip install --no-cache-dir "mlflow==${MLFLOW_VERSION}" psycopg2-binary

  COPY packages/ml/mlflow_bootstrap_handler.py ${LAMBDA_TASK_ROOT}/handler.py
  COPY assets/rds-ca-bundle.pem ${LAMBDA_TASK_ROOT}/rds-ca-bundle.pem

  CMD ["handler.handler"]