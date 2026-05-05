from mangum import Mangum

from match_predictor_api.main import app

_mangum_handler = Mangum(app, api_gateway_base_path="api")


def handler(event, context):
    if event.get("source") == "lambda.warmup":
        return {"warm": True}
    return _mangum_handler(event, context)
