# cutting.scot: ECS → static S3/CloudFront cutover (minimal downtime)

The CloudFront distribution is managed by `WebsiteStack`, so `cdk deploy` updates it in place — no DNS/cert change. Downtime is only the gap between the origin flipping to the (empty) bucket and the `s3 sync` finishing. Build first so that gap is seconds.

Account `313095418189`, region `us-east-1`.

## 1. Build the static site first (so it's ready to sync the moment the bucket exists)

```
pnpm --filter @cutting/website build
```

## 2. Deploy the stack — creates the bucket, flips CloudFront origin ALB→S3, destroys ECS/ALB

```
cdk deploy WebsiteStack --require-approval never --app "python3 packages/deploy/app.py"
```

(Run from the match-predictor repo root. The website build output is in the cuttingedge repo at `apps/website/dist/client`.)

## 3. Immediately populate the bucket and invalidate

```
aws s3 sync /Users/paulcowan/projects/cuttingedge/apps/website/dist/client "s3://cutting-scot-site-313095418189" --delete
aws cloudfront create-invalidation --distribution-id "$(aws cloudfront list-distributions --query "DistributionList.Items[?contains(Aliases.Items, 'cutting.scot')].Id" --output text)" --paths "/*"
```

## 4. Verify

```
curl -I https://cutting.scot
curl -sL https://cutting.scot/oss/ | grep -o '<title>[^<]*</title>'
```

## 5. Cleanup

- Delete the now-unused CDK files: `packages/deploy/deploy/website_stack/alb.py`, `ecs.py`, `network.py`.
- If the deploy stalls deleting security groups (lingering Fargate ENIs), wait ~20 min and re-run the deploy, or delete the detached ENIs — same as the DeployStack teardown.

## Zero downtime instead (optional, more steps)

Split step 2: first deploy only adds the bucket (comment out the origin flip), run step 3 to fill it, then a second deploy flips the origin and deletes ECS/ALB. Not worth it unless the brief outage matters.
