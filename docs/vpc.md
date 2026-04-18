# VPC

## Check VPCs exist

```bash
aws ec2 describe-vpcs \
  --query "Vpcs[?Tags[?Key=='Name']].{Id:VpcId,Cidr:CidrBlock,State:State,Tags:Tags[?Key=='Name'].Value|[0]}" \
  --output table
```

## List subnets in a VPC

```bash
aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=vpc-08a168d94d0616192" \
  --query "Subnets[].{Id:SubnetId,IPv4:CidrBlock,IPv6:Ipv6CidrBlockAssociationSet[0].Ipv6CidrBlock,Az:AvailabilityZone,Public:MapPublicIpOnLaunch}" \
  --output table
```

## List security groups in a VPC

```bash
aws ec2 describe-security-groups \
  --filters "Name=vpc-id,Values=<vpc-id>" \
  --query "SecurityGroups[].{Id:GroupId,Name:GroupName,Description:Description}" \
  --output table
```

## Check IPv6 CIDR on VPC

```bash
aws ec2 describe-vpcs \
  --vpc-ids vpc-08a168d94d0616192 \
  --query "Vpcs[0].Ipv6CidrBlockAssociationSet" \
  --output json
```

## Check NAT gateways

```bash
aws ec2 describe-nat-gateways \
  --query "NatGateways[].{Id:NatGatewayId,State:State,Subnet:SubnetId}" \
  --output table
```

## List VPC endpoints

```bash
aws ec2 describe-vpc-endpoints \
  --filters "Name=vpc-id,Values=vpc-08a168d94d0616192" \
  --query "VpcEndpoints[].{Id:VpcEndpointId,Service:ServiceName,State:State}" \
  --output table
```

## Delete a VPC endpoint

```bash
aws ec2 delete-vpc-endpoints --vpc-endpoint-ids vpce-01830162d1283a68b
```
