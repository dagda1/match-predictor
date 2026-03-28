from constructs import Construct
from aws_cdk.aws_lambda_python_alpha import PythonFunction

class Queuing(Construct):
    def __init__(self, scope: Construct, construct_id: str, predictor_function: PythonFunction) -> None:
        super().__init__(scope, construct_id)

        # TODO: Implement queuing system
        pass
