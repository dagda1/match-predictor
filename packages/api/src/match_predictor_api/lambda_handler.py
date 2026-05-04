from mangum import Mangum

from match_predictor_api.main import app

handler = Mangum(app, api_gateway_base_path="api")
