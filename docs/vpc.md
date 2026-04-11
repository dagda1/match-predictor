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
  --filters "Name=vpc-id,Values=<vpc-id>" \
  --query "Subnets[].{Id:SubnetId,Cidr:CidrBlock,Az:AvailabilityZone,Public:MapPublicIpOnLaunch}" \
  --output table
```

## List security groups in a VPC

```bash
aws ec2 describe-security-groups \
  --filters "Name=vpc-id,Values=<vpc-id>" \
  --query "SecurityGroups[].{Id:GroupId,Name:GroupName,Description:Description}" \
  --output table
```

## Check NAT gateways

```bash
aws ec2 describe-nat-gateways \
  --query "NatGateways[].{Id:NatGatewayId,State:State,Subnet:SubnetId}" \
  --output table
```
