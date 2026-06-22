# Verify all Fargate / ALB is gone (website + frontendsupport)

Region `us-east-1`. Anything that still lists `website` or `frontendsupport` is not deleted yet.

## ECS clusters and services

```
aws ecs list-clusters --region us-east-1 --output text
```

Neither `website` nor `frontendsupport` should appear. If a cluster still shows, check for services:

```
aws ecs list-services --region us-east-1 --cluster website --output text
aws ecs list-services --region us-east-1 --cluster frontendsupport --output text
```

## Load balancers

```
aws elbv2 describe-load-balancers --region us-east-1 --query "LoadBalancers[].LoadBalancerName" --output text
```

No `website`/`frontendsupport` ALB should appear.

## Running Fargate tasks (account-wide quick check)

```
aws resourcegroupstaggingapi get-resources --region us-east-1 --resource-type-filters ecs:cluster ecs:service elasticloadbalancing:loadbalancer --query "ResourceTagMappingList[].ResourceARN" --output text
```

Empty (or nothing website/frontendsupport related) = both are fully torn down.
