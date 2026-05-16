FROM public.ecr.aws/lambda/python:3.13

RUN pip install --no-cache-dir psycopg2-binary

COPY handler.py ${LAMBDA_TASK_ROOT}/
COPY sql ${LAMBDA_TASK_ROOT}/sql
COPY rds-ca-bundle.pem ${LAMBDA_TASK_ROOT}/rds-ca-bundle.pem

CMD ["handler.handler"]
