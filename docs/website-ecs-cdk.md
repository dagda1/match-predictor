# Website → ECS Fargate (CDK)

Migrate `apps/website` (currently DigitalOcean droplet) onto ECS Fargate behind ALB + CloudFront. Built as CDK in this repo for learning. Domain swap is the **last** step — everything below comes up on AWS-owned hostnames and touches nothing public.

## Build order (bottom-up by dependency)

1. **Network** — reuse default VPC (`Vpc.from_lookup`). Two security groups:
   - ALB SG: ingress HTTP:80 from CloudFront's managed prefix list (`com.amazonaws.global.cloudfront.origin-facing`).
   - Task SG: ingress on app port (3000) from the ALB SG only.

2. **ALB** — `aws_lb` (internet-facing) + target group (`target_type=ip`, port 3000, health check `/`) + HTTP:80 listener → target group. Target group is empty/unhealthy until a task registers; that's expected.

3. **ECS cluster + task definition** — Fargate, container = `website_server` ECR image, awslogs driver, 1 vCPU / 2 GB (puppeteer needs headroom).

4. **ECS service** — Fargate, desired_count 1, attached to the target group, `assign_public_ip=true` (default VPC). This is the step that makes the target go healthy.

5. **CloudFront** — single ALB origin over HTTP (`origin_protocol_policy=http-only`). SSR default behaviour `Managed-CachingDisabled`; `/assets/*` behaviour `Managed-CachingOptimized` (Vite hashed assets). Viewer cert deferred (domain last).

In CDK you don't hand-order resources — pass references (the service takes the target group object) and CDK derives deploy order. "ALB first" just means the target group object must exist before the service that registers into it.

## Verify (no DNS needed)

- ALB target health → `["healthy"]`.
- ECS service rollout → `"COMPLETED"`.
- `curl -I https://<dist>.cloudfront.net/` → 200, `via:` header names CloudFront.
- Smoke test with `/etc/hosts` override (`<cloudfront-edge-ip> cutting.scot`): SSR page renders, puppeteer OG-image route returns a PNG.

## Domain (LAST — see route53-cutting-scot.md)

Only after the stack is verified: ACM cert (validation CNAME added manually at DigitalOcean while NS still points there), swap NS at 34SP, add apex ALIAS → CloudFront.
