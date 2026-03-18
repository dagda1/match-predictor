from aws_cdk.aws_glue_alpha import S3Table, Database, Schema, DataFormat, Column  
from aws_cdk import aws_s3 as s3
from constructs import Construct

class DataStorage(Construct):
    def __init__(self, scope: Construct, construct_id: str, bucket: s3.Bucket) -> None:
        super().__init__(scope, construct_id)

        database = Database(self, "Database", database_name="match_predictor")

        matches_table = S3Table(self, "MatchesTable",
                database=database,
                bucket=bucket,
                table_name="matches",
                columns=[
                    Column(name="id", type=Schema.STRING),
                    Column(name="date", type=Schema.TIMESTAMP),
                    Column(name="season", type=Schema.STRING),
                    Column(name="homeTeam", type=Schema.STRING),
                    Column(name="awayTeam", type=Schema.STRING),
                    Column(name="homeGoals", type=Schema.INTEGER),
                    Column(name="awayGoals", type=Schema.INTEGER),
                    Column(name="homeXg", type=Schema.DOUBLE),
                    Column(name="awayXg", type=Schema.DOUBLE),
                    Column(name="homeShots", type=Schema.INTEGER),
                    Column(name="awayShots", type=Schema.INTEGER),
                    Column(name="homeShotsOnTarget", type=Schema.INTEGER),
                    Column(name="awayShotsOnTarget", type=Schema.INTEGER),
                    Column(name="homeDeep", type=Schema.INTEGER),
                    Column(name="awayDeep", type=Schema.INTEGER),
                    Column(name="homePpda", type=Schema.DOUBLE),
                    Column(name="awayPpda", type=Schema.DOUBLE),
                    Column(name="homeWinProb", type=Schema.DOUBLE),
                    Column(name="drawProb", type=Schema.DOUBLE),
                    Column(name="awayWinProb", type=Schema.DOUBLE),
                ],
                data_format=DataFormat.JSON
        )

        shared = [
            Column(name="homeWin", type=Schema.DOUBLE),
            Column(name="draw", type=Schema.DOUBLE),
            Column(name="awayWin", type=Schema.DOUBLE),
            Column(name="predictedOutcome", type=Schema.STRING),
            Column(name="correct", type=Schema.BOOLEAN),
            Column(name="topScore", type=Schema.struct([
                Column(name="homeGoals", type=Schema.INTEGER),
                Column(name="awayGoals", type=Schema.INTEGER),
                Column(name="probability", type=Schema.DOUBLE),
            ])),
        ]

        ml_struct = Schema.struct(shared)
        poisson_struct = Schema.struct(shared + [
            Column(name="homeLambda", type=Schema.DOUBLE),
            Column(name="awayLambda", type=Schema.DOUBLE),
        ])
        
        predictions_table = S3Table(self, "PredictionsTable",
                database=database,
                bucket=bucket,
                table_name="predictions",
                columns=[
                    Column(name="homeTeam", type=Schema.STRING),
                    Column(name="awayTeam", type=Schema.STRING),
                    Column(name="date", type=Schema.TIMESTAMP),
                    Column(name="actualHomeGoals", type=Schema.INTEGER),
                    Column(name="actualAwayGoals", type=Schema.INTEGER),
                    Column(name="actualOutcome", type=Schema.STRING),
                    Column(name="ml", type=ml_struct),
                    Column(name="poisson", type=poisson_struct)
                ],
                data_format=DataFormat.JSON
        )

        upcoming_table = S3Table(self, "UpcomingTable",
                database=database,
                bucket=bucket,
                table_name="upcoming",
                columns=[
                    Column(name="homeTeam", type=Schema.STRING),
                    Column(name="awayTeam", type=Schema.STRING),
                    Column(name="date", type=Schema.TIMESTAMP),
                    Column(name="ml", type=ml_struct),
                    Column(name="poisson", type=poisson_struct)
                ],
                data_format=DataFormat.JSON
        )
