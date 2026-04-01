from aws_cdk import Stack, aws_s3 as s3, Duration, RemovalPolicy
from constructs import Construct

class Storage(Construct):
    def __init__(self, scope: Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)

        base_name = f"cuttingedge-matchpredictor-data-{Stack.of(self).region}-{Stack.of(self).account}" 

        log_bucket = s3.Bucket(self, "AccessLogBucket",
            bucket_name=f"{base_name}-logs",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=False,
            removal_policy=RemovalPolicy.DESTROY,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
            lifecycle_rules=[
                s3.LifecycleRule(
                    expiration=Duration.days(30)
                )
            ]
        )   
        
        self.bucket: s3.Bucket = s3.Bucket(self, "Bucket",
            bucket_name=base_name,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            versioned=False,
            removal_policy=RemovalPolicy.DESTROY,
            server_access_logs_bucket=log_bucket,
            lifecycle_rules=[                                                                                                                          
                s3.LifecycleRule(                                                                                                                   
                    transitions=[                                                                                                                   
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=Duration.days(30)                                                                                      
                        ),
                        s3.Transition(                                                                                                              
                            storage_class=s3.StorageClass.GLACIER,
                            transition_after=Duration.days(90)                                                                                      
                        )
                    ]                                                                                                                               
                )                                                                                                                                   
            ] 
        )

        self.frontend_bucket: s3.Bucket = s3.Bucket(self, "FrontendBucket",
            bucket_name=f"{base_name}-frontend",
            versioned=False,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            auto_delete_objects=True
        )