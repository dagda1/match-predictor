from aws_cdk import (
    CfnOutput,
    Stack,
    aws_iam as iam,
    custom_resources as cr,
)
from constructs import Construct
from deploy.deploy_stack.storage import Storage
from deploy.deploy_stack.data_storage import DataStorage
from deploy.deploy_stack.functions import EtlFunctions
from deploy.deploy_stack.events import Events
from deploy.deploy_stack.alerts import Alerts
from deploy.deploy_stack.queuing import Queuing
from deploy.deploy_stack.api import Api
from deploy.deploy_stack.cdn import Cdn
from deploy.deploy_stack.secrets import Secrets
from deploy.deploy_stack.database import Database
from deploy.deploy_stack.vpc import Vpc
from deploy.deploy_stack.bootstrap import Bootstrap
from deploy.deploy_stack.migration import Migration
from deploy.deploy_stack.model_storage import ModelStorage
from deploy.deploy_stack.firehose import Firehose
from deploy.deploy_stack.firehose_lambda import FirehoseFunctions
from deploy.deploy_stack.glue import Glue
from deploy.deploy_stack.mlflow import Mlflow

class DeployStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, certificate, hosted_zone, web_acl_arn, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        github_provider = iam.OpenIdConnectProvider(
                self, "GitHubProvider",
                url="https://token.actions.githubusercontent.com",
                client_ids=["sts.amazonaws.com"],
                thumbprints=["6938fd4d98bab03faadb97b34396831e3780aea1"]
            )

        provider_role = iam.Role(
            self, "GitHubActionRole",
            assumed_by=iam.OpenIdConnectPrincipal(
                github_provider,
                conditions={
                    "StringLike": {
                        "token.actions.githubusercontent.com:sub": "repo:dagda1/match-predictor:*"
                    }
                }
            ),
            description="Role assumed by GitHub Actions"
        )

        provider_role.add_to_policy(
            iam.PolicyStatement(
                actions=["sts:AssumeRole"],
                resources=[f"arn:aws:iam::{self.account}:role/cdk-hnb659fds-*"]
            )
        )

        provider_role.add_to_policy(
            iam.PolicyStatement(
                actions=["cloudformation:DescribeStacks"],
                resources=[self.stack_id]
            )
        )

        network = Vpc(self, "Network")

        database = Database(self, "Database",
            vpc=network.vpc,
            security_group=network.database_security_group,
        )

        bootstrap = Bootstrap(self, "DatabaseBootstrap",
            database=database.instance,
            vpc=network.vpc,
            security_group=network.lambda_security_group,
        )
        CfnOutput(self, "BootstrapFunctionName", value=bootstrap.function.function_name)

        migration = Migration(self, "DatabaseMigration",
            database=database.instance,
            vpc=network.vpc,
            security_group=network.lambda_security_group,
        )

        mlflow = Mlflow(self, "Mlflow",
            database=database.instance,
            vpc=network.vpc,
            security_group=network.lambda_security_group,
        )
        CfnOutput(self, "MlflowFunctionName", value=mlflow.function.function_name)

        storage = Storage(self, "Storage")
        DataStorage(self, "DataStorage", bucket=storage.bucket)

        network.s3_endpoint.add_to_policy(
            iam.PolicyStatement(
                principals=[iam.AnyPrincipal()],
                actions=["s3:GetObject", "s3:PutObject", "s3:ListBucket", "s3:DeleteObject"],
                resources=[
                    storage.bucket.bucket_arn,
                    f"{storage.bucket.bucket_arn}/*",
                ],
            )
        )

        model_storage = ModelStorage(self, "ModelStorage",
            vpc=network.vpc,
            lambda_security_group=network.lambda_security_group,
        )

        functions=EtlFunctions(self, "EtlFunctions",
            bucket=storage.bucket,
            database=database.instance,
            model_storage=model_storage,
            vpc=network.vpc,
            security_group=network.lambda_security_group,
        )
        Queuing(self, "Queuing", scraper=functions.scraper, predictor=functions.predictor)
        Events(self, "EventBridge", scraper_function=functions.scraper)

        initial_data_load = cr.AwsCustomResource(self, "InitialDataLoad",
            install_latest_aws_sdk=False,
            on_create=cr.AwsSdkCall(
                service="Lambda",
                action="invoke",
                parameters={
                    "FunctionName": functions.scraper.function_name,
                    "InvocationType": "Event",
                },
                physical_resource_id=cr.PhysicalResourceId.of("InitialDataLoad"),
            ),
            policy=cr.AwsCustomResourcePolicy.from_statements([
                iam.PolicyStatement(
                    actions=["lambda:InvokeFunction"],
                    resources=[functions.scraper.function_arn],
                )
            ],
            )
        )
        initial_data_load.node.add_dependency(functions.scraper)
        initial_data_load.node.add_dependency(migration)

        storage.frontend_bucket.grant_read_write(provider_role)

        app_secrets = Secrets(self, "Secrets")

        api = Api(self, "Api",
            bucket=storage.bucket,
            origin_verify_secret=app_secrets.origin_verify,
            model_storage=model_storage,
            database=database.instance,
            vpc=network.vpc,
            security_group=network.lambda_security_group,
        )

        cdn = Cdn(self, "Cdn",
            frontend_bucket=storage.frontend_bucket,
            certificate=certificate,
            hosted_zone=hosted_zone,
            http_api=api.http_api,
            origin_verify_secret=app_secrets.origin_verify.secret_value.unsafe_unwrap(),
            web_acl_arn=web_acl_arn,
        )

        provider_role.add_to_policy(
            iam.PolicyStatement(
                actions=["cloudfront:CreateInvalidation"],
                resources=[f"arn:aws:cloudfront::{self.account}:distribution/{cdn.distribution.distribution_id}"],
            )
        )

        CfnOutput(self, "FrontendBucketName", value=storage.frontend_bucket.bucket_name)
        
        firehose_functions = FirehoseFunctions(self, "FirehoseFunctions")
    
        firehose = Firehose(self, "Firehose", storage.bucket, firehose_functions.transformer)
        firehose.subscribe(api.function.log_group)
        CfnOutput(self, "FirehoseDeliveryStreamName", value=firehose.firehose.delivery_stream_name)
        
        glue_catalog = Glue(self, "Glue", storage.bucket)
        CfnOutput(self, "GlueLogsTableName", value=glue_catalog.logs_table.ref)
        