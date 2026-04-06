from aws_cdk import aws_secretsmanager as secretsmanager
from constructs import Construct


class Secrets(Construct):
    def __init__(self, scope: Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)

        self.origin_verify = secretsmanager.Secret(self, "OriginVerifySecret",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                exclude_punctuation=True,
                password_length=64,
            ),
        )
