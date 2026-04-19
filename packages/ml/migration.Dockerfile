FROM public.ecr.aws/lambda/python:3.13

RUN pip install --no-cache-dir alembic sqlalchemy psycopg2-binary

COPY alembic.ini ${LAMBDA_TASK_ROOT}/
COPY alembic ${LAMBDA_TASK_ROOT}/alembic

RUN mkdir -p ${LAMBDA_TASK_ROOT}/match_predictor && \
    touch ${LAMBDA_TASK_ROOT}/match_predictor/__init__.py

COPY src/match_predictor/db_models.py ${LAMBDA_TASK_ROOT}/match_predictor/db_models.py
COPY migration_handler.py ${LAMBDA_TASK_ROOT}/handler.py

CMD ["handler.handler"]
