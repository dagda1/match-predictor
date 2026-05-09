from constructs import Construct
from aws_cdk import (
    aws_lambda,
    Duration
)
from aws_cdk.aws_lambda_nodejs import (
    NodejsFunction,
    OutputFormat,
    BundlingOptions
)
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[4]

class FirehoseFunctions(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
    ) -> None:
        super().__init__(scope, construct_id)

        self.transformer = NodejsFunction(self, "LogTransformerFunction",
            entry=str(REPO_DIR / "packages" / "etl" / "src" / "log-transform-handler.ts"),
            project_root=str(REPO_DIR),
            deps_lock_file_path=str(REPO_DIR / "pnpm-lock.yaml"),
            handler="handler",
            runtime=aws_lambda.Runtime.NODEJS_24_X,
            timeout=Duration.minutes(5),
            tracing=aws_lambda.Tracing.ACTIVE,
            memory_size=512,
            bundling=BundlingOptions(
                format=OutputFormat.ESM,
            ),
        )