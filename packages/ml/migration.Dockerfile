FROM public.ecr.aws/lambda/python:3.13

RUN pip install --no-cache-dir alembic sqlalchemy psycopg2-binary

COPY packages/ml/alembic.ini ${LAMBDA_TASK_ROOT}/
COPY packages/ml/alembic ${LAMBDA_TASK_ROOT}/alembic

RUN mkdir -p ${LAMBDA_TASK_ROOT}/match_predictor && \
    touch ${LAMBDA_TASK_ROOT}/match_predictor/__init__.py

COPY packages/ml/src/match_predictor/db_models.py ${LAMBDA_TASK_ROOT}/match_predictor/db_models.py
COPY packages/ml/migration_handler.py ${LAMBDA_TASK_ROOT}/handler.py
COPY assets/rds-ca-bundle.pem ${LAMBDA_TASK_ROOT}/rds-ca-bundle.pem

CMD ["handler.handler"]
