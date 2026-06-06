from aws_cdk import (
    CfnOutput,
    Duration,
    aws_elasticloadbalancingv2 as elbv2,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
)
from constructs import Construct


class Cdn(Construct):
    def __init__(self, scope: Construct, construct_id: str, alb: elbv2.ApplicationLoadBalancer) -> None:
        super().__init__(scope, construct_id)

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

        origin = origins.LoadBalancerV2Origin(alb,
            protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
        )

        self.distribution = cloudfront.Distribution(self, "Distribution",
            comment="cutting.scot website",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origin,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=no_cache_policy,
                origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
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
