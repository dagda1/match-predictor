from aws_cdk import (
    CfnOutput,
    Duration,
    Fn,
    aws_apigatewayv2 as apigw,
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_s3 as s3,
)
from constructs import Construct

from deploy.certificate import DOMAIN_NAME

ORIGIN_VERIFY_HEADER = "x-origin-verify"


class Cdn(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        frontend_bucket: s3.Bucket,
        certificate: acm.ICertificate,
        hosted_zone: route53.IHostedZone,
        http_api: apigw.HttpApi,
        origin_verify_secret: str,
        web_acl_arn: str,
    ) -> None:
        super().__init__(scope, construct_id)

        oac = cloudfront.S3OriginAccessControl(self, "OAC")

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

        api_domain = Fn.select(2, Fn.split("/", http_api.url))
        api_origin = origins.HttpOrigin(api_domain,
            custom_headers={ORIGIN_VERIFY_HEADER: origin_verify_secret},
        )

        s3_origin = origins.S3BucketOrigin.with_origin_access_control(
            frontend_bucket,
            origin_access_control=oac,
        )

        self.distribution = cloudfront.Distribution(self, "Distribution",
            comment="match-predictor frontend",
            domain_names=[DOMAIN_NAME],
            certificate=certificate,
            default_behavior=cloudfront.BehaviorOptions(
                origin=s3_origin,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=no_cache_policy,
            ),
            additional_behaviors={
                "/assets/*": cloudfront.BehaviorOptions(
                    origin=s3_origin,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    cache_policy=asset_cache_policy,
                ),
                "/api/*": cloudfront.BehaviorOptions(
                    origin=api_origin,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                ),
            },
            default_root_object="index.html",
            http_version=cloudfront.HttpVersion.HTTP3,
            web_acl_id=web_acl_arn,
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
            ],
        )

        route53.ARecord(self, "AliasRecord",
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(self.distribution)),
        )

        CfnOutput(scope, "DistributionId", value=self.distribution.distribution_id)
        CfnOutput(scope, "DistributionDomain", value=self.distribution.distribution_domain_name)
