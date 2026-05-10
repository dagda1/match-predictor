from aws_cdk import (
    aws_glue as glue,
    aws_s3 as s3,
    Stack
)
from constructs import Construct

class Glue(Construct):
    def __init__(self, scope: Construct, construct_id: str, bucket: s3.Bucket):
        super().__init__(scope, construct_id)

        self.database = glue.CfnDatabase(
            self,
            "LogsDatabase",
            catalog_id=Stack.of(self).account,
            database_input={
                "name": "logs",
            },
        )

        self.logs_table = glue.CfnTable(
            self,
            "LogsTable",
            database_name="logs",
            catalog_id=Stack.of(self).account,
            table_input={
                "name": "logs",
                "storageDescriptor": {
                    "columns": [
                        {"name": "event_time", "type": "bigint"},
                        {"name": "message", "type": "string"},
                        {"name": "log_group", "type": "string"},
                        {"name": "log_stream", "type": "string"},
                    ],
                    "location": bucket.s3_url_for_object("logs/"),
                    "inputFormat": "org.apache.hadoop.mapred.TextInputFormat",
                    "outputFormat": "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat",
                    "serdeInfo": {
                        "serializationLibrary": "org.openx.data.jsonserde.JsonSerDe",
                        "parameters": {
                            "mapping.event_time": "timestamp",
                            "mapping.message": "message",
                            "mapping.log_group": "logGroup",
                            "mapping.log_stream": "logStream",
                        }
                    },
                },
            },
        )

        self.logs_table.add_depends_on(self.database)
