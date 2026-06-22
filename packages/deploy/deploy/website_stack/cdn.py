from aws_cdk import (
    CfnOutput,
    Duration,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_certificatemanager as acm,
)
from constructs import Construct

DOMAIN_NAME = "cutting.scot"
CERTIFICATE_ARN = "arn:aws:acm:us-east-1:313095418189:certificate/6fa707bc-01eb-4b1d-ab8c-38be4e2d7585"


class Cdn(Construct):
    def __init__(self, scope: Construct, construct_id: str, bucket: s3.Bucket) -> None:
        super().__init__(scope, construct_id)

        certificate = acm.Certificate.from_certificate_arn(self, "Certificate", CERTIFICATE_ARN)

        asset_cache_policy = cloudfront.CachePolicy(self, "AssetCachePolicy",
            default_ttl=Duration.days(365),
            max_ttl=Duration.days(365),
            min_ttl=Duration.days(365),
            enable_accept_encoding_brotli=True,
            enable_accept_encoding_gzip=True,
        )

        no_cache_policy = cloudfront.CachePolicy(self, "NoCachePolicy",
            default_ttl=Duration.seconds(0),
            max_ttl=Duration.seconds(0),
            min_ttl=Duration.seconds(0),
        )

        origin = origins.S3StaticWebsiteOrigin(bucket,
            protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
        )

        self.distribution = cloudfront.Distribution(self, "Distribution",
            comment="cutting.scot website",
            domain_names=[DOMAIN_NAME],
            certificate=certificate,
            default_root_object="index.html",
            minimum_protocol_version=cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
            default_behavior=cloudfront.BehaviorOptions(
                origin=origin,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=no_cache_policy,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD_OPTIONS,
            ),
            additional_behaviors={
                "/assets/*": cloudfront.BehaviorOptions(
                    origin=origin,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    cache_policy=asset_cache_policy,
                ),
                "/static/*": cloudfront.BehaviorOptions(
                    origin=origin,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    cache_policy=asset_cache_policy,
                ),
            },
            http_version=cloudfront.HttpVersion.HTTP3,
        )

        CfnOutput(scope, "WebsiteDistributionId", value=self.distribution.distribution_id)
        CfnOutput(scope, "WebsiteDistributionDomain", value=self.distribution.distribution_domain_name)
