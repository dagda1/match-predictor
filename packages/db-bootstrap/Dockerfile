FROM public.ecr.aws/lambda/python:3.13

RUN pip install --no-cache-dir psycopg2-binary

COPY handler.py ${LAMBDA_TASK_ROOT}/
COPY sql ${LAMBDA_TASK_ROOT}/sql

CMD ["handler.handler"]
