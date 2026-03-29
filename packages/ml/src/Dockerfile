FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY match_predictor/ match_predictor/

CMD ["match_predictor.lambda_handler.handler"]
