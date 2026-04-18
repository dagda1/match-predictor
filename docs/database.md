# Database

## Check RDS instance status

```bash
aws rds describe-db-instances \
  --query "DBInstances[].{Id:DBInstanceIdentifier,Status:DBInstanceStatus,Engine:Engine,Endpoint:Endpoint.Address,Port:Endpoint.Port}" \
  --output table
```
do 