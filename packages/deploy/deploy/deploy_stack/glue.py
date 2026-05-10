from aws_cdk import (
    aws_glue as glue,
    aws_s3 as s3,
    Stack
)
from constructs import Construct

class Glue(Construct):
    def __init__(self, scope: Construct, construct_id: str, bucket: s3.Bucket):
        super().__init__(scope, construct_id)

        self.logs_table = glue.CfnTable(
            self,
            "LogsTable",
            database_name="logs",
            catalog_id=Stack.of(self).account,
            table_input={
                "name": "logs",
                "storageDescriptor": {
                    "columns": [
                        {"name": "timestamp", "type": "bigint"},
                        {"name": "message", "type": "string"},
                        {"name": "logGroup", "type": "string"},
                        {"name": "logStream", "type": "string"},
                    ],
                    "location": bucket.s3_url_for_object("logs"),
                    "inputFormat": "org.apache.hadoop.mapred.TextInputFormat",
                    "outputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                    "serdeInfo": {
                        "serializationLibrary": "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe",
                    },
                },
            },
        )
