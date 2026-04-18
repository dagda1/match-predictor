# AWS MLA-C01 — Machine Learning Engineer Associate

Source: https://docs.aws.amazon.com/aws-certification/latest/examguides/machine-learning-engineer-associate-01.html

Exam: $150, 65 questions, 130 minutes, pass 720/1000

## Context for agents

- Paul is a frontend dev pivoting to MLOps
- He knows: programming (not Python), Docker, Terraform, CI/CD, Linux
- He does NOT know: Python syntax, AWS ML services, ML theory beyond basics
- He learns by doing, not videos or books
- Each service checkbox gets sub-tasks tied to this repo (match-predictor)
- All infrastructure must be done with CDK or CloudFormation — no web console, no Terraform
- Do NOT generate code for him — answer questions, check his work, explain errors
- Do NOT make assumptions or state things as fact without a source
- Do NOT write walls of text
- Checked boxes = done. Work top to bottom. Resume from the first unchecked item.

## In-scope AWS services

Source: https://docs.aws.amazon.com/aws-certification/latest/examguides/mla-01-in-scope-services.html

### commands
  - `aws iam list-roles --query "Roles[?starts_with(CreateDate, '2026-03-07')].[RoleName, Arn]" --output table`

### Analytics

- [ ] Amazon Athena
  - [X] Create a CDK project in `packages/deploy` (Python)
     - created with `cdk init app --language python`
  - [X] Set up GitHub Actions OIDC trust (one-time local deploy):
    - [X] Add GitHub OIDC identity provider to CDK stack
    - [X] Add IAM role that GitHub Actions can assume via OIDC
    - [X] `cdk deploy` once from laptop to bootstrap CI credentials
    - [X] Add GitHub Actions workflow that assumes the role and runs `cdk deploy`
    - [X] Verify: push a commit and confirm CI deploys successfully
  - [X] Create an IAM role for bucket access
    - skipped: CDK best practice is to use grant methods when a consumer exists, not pre-create roles
  - [X] Define an S3 bucket in CDK with production-grade settings:
    - [X] Block all public access
    - [X] Encryption at rest (SSE-S3 or KMS)
    - [X] Enforce SSL (reject non-HTTPS)
    - [X] Versioning enabled
    - [X] Lifecycle rules (move old data to cheaper tiers)
    - [X] Access logging
    - [X] Least privilege IAM policy (attach to IAM role)
      - skipped: will use CDK grant methods when consumer (Lambda) is created
  - [X] Verify with `cdk synth` (like `terraform plan`)
  - [X] Deploy with `cdk deploy`
  - [X] Bootstrap initial data into S3:
    - [X] Run scraper locally: `pnpm refresh`
    - [X] Upload output to S3 with AWS CLI: `./scripts/upload-data.sh`
  - [X] Create a Glue table definition for the match schema
  - [X] Query match data with SQL in Athena
  - [X] Understand when to use Athena vs pandas (cost, scale, serverless)
  - [ ] Automate daily ETL (replaces manual scraper runs):
    - [X] TypeScript Lambda — imports existing scraper, writes matches to S3
    - [X] EventBridge rule — cron schedule triggers scraper Lambda daily at 06:00 UTC
    - [X] CDK constructs for scraper Lambda and EventBridge in `packages/deploy/deploy/etl/`
    - [X] Verify scraper Lambda runs successfully
    - [X] Refactor Python generate() functions to accept read/write functions (pluggable storage)
    - [X] Python Lambda — imports existing generate_predictions/generate_upcoming, reads matches from S3, writes predictions + upcoming to S3
    - [X] SQS queue — scraper Lambda sends message on completion, triggers Python Lambda
    - [X] SNS notifications on success and CloudWatch alarms on error
    - [X] X-Ray tracing enabled on both Lambdas
    - [X] Verify full pipeline runs: EventBridge → scraper → SQS → predictor → S3
  - [ ] Deploy web app to AWS:
    - [X] Frontend: build React app, deploy to S3 + CloudFront
    - [X] API: deploy FastAPI as Lambda behind API Gateway
    - [X] Single CloudFront distribution serves both frontend (S3) and API (API Gateway)
    - [X] API Gateway only accessible through CloudFront (not directly)
    - [X] WAF with rate limiting on CloudFront to prevent abuse
    - [X] CloudFront: HTTP/3, Brotli compression
    - [X] Cache: index.html `no-cache` (always revalidate), hashed assets `max-age=31536000, immutable`
    - [X] CDK constructs for CloudFront, S3 static hosting, API Gateway, Lambda, WAF
    - [X] CDK stack outputs: frontend bucket name, CloudFront distribution ID
    - [X] GitHub Actions: build React, cdk deploy, s3 sync, CloudFront invalidation (index.html only)
    - [X] Wire frontend to use relative `/api/*` paths through CloudFront
    - [X] Custom domain (optional)
    - [ ] Lambda@Edge for origin verify secret — read from Secrets Manager at request time, enables auto-rotation without redeploy
  - [ ] Move API data to Postgres (RDS):
    - [X] Docker compose with Postgres 17 for local dev
    - [X] SQLAlchemy models in `packages/ml/src/match_predictor/db_models.py`: Team, Match, TeamFeatures, Prediction, Upcoming
    - [X] Alembic migrations in `packages/ml/alembic/`
    - [X] API reads from Postgres locally — `packages/api/src/match_predictor_api/db.py` connects via `DATABASE_URL` env var
    - [X] Seed script `scripts/seed-db.py` — clears tables then seeds from JSON files
    - [X] `pnpm setup:local` — docker compose, refresh, migrate, seed
    - [X] `pnpm dev` — starts Postgres, API (port 4400), frontend (port 3300)
    - [X] Poisson back in `/predict` — queries match history from Postgres via `load_matches_dataframe()`
    - [X] CDK: VPC with dual-stack IPv6, public + private subnets, NAT gateway — `deploy_stack/vpc.py`
    - [X] CDK: Security groups — Lambda SG → Database SG on port 5432 — `deploy_stack/vpc.py`
    - [X] CDK: RDS Postgres 18.3 `db.t4g.micro` in VPC private subnets — `deploy_stack/database.py`
    - [X] Put Lambdas in VPC — add `vpc`, `vpc_subnets`, `security_groups` to Lambda constructs in `functions.py` and `api.py`
    - [ ] IAM auth for Lambda → RDS connection (no passwords)
    - [ ] Pass `DATABASE_URL` to API Lambda and predictor Lambda as env var
    - [ ] Migration Lambda — runs `alembic upgrade head` after deploy
    - [ ] Predictor Lambda writes to Postgres instead of S3 JSON files
    - [ ] Seed Lambda or migration step — initial data load into RDS
    - [ ] API Lambda reads from Postgres in AWS (already works, just needs `DATABASE_URL`)
    - [ ] Model file stays in S3 (binary blob, loaded on cold start)
    - [ ] Remove S3 JSON file reading from API
    - [ ] Add `psycopg2-binary` and `sqlalchemy` to API Dockerfile
- [ ] Amazon Data Firehose
- [ ] Amazon EMR
- [ ] AWS Glue
- [ ] AWS Glue DataBrew
- [ ] AWS Glue Data Quality
- [ ] Amazon Kinesis
- [ ] AWS Lake Formation
- [ ] Amazon Managed Service for Apache Flink
- [ ] Amazon OpenSearch Service
- [ ] Amazon QuickSight
- [ ] Amazon Redshift

### Application Integration

- [ ] Amazon EventBridge (covered by daily ETL)
- [ ] Amazon MWAA (Managed Workflows for Apache Airflow)
- [ ] Amazon SNS
- [ ] Amazon SQS (covered by daily ETL)
- [ ] AWS Step Functions

### Cloud Financial Management

- [ ] AWS Billing and Cost Management
- [ ] AWS Budgets
- [ ] AWS Cost Explorer

### Compute

- [ ] AWS Batch
- [ ] Amazon EC2
- [ ] AWS Lambda
- [ ] AWS Serverless Application Repository

### Containers

- [ ] Amazon ECR
- [ ] Amazon ECS
- [ ] Amazon EKS

### Database

- [ ] Amazon DocumentDB
- [ ] Amazon DynamoDB
- [ ] Amazon ElastiCache
- [ ] Amazon Neptune
- [ ] Amazon RDS

### Developer Tools

- [ ] AWS CDK
- [ ] AWS CodeArtifact
- [ ] AWS CodeBuild
- [ ] AWS CodeDeploy
- [ ] AWS CodePipeline
- [ ] AWS X-Ray

### Machine Learning

- [ ] Amazon A2I (Augmented AI)
- [ ] Amazon Bedrock
- [ ] Amazon CodeGuru
- [ ] Amazon Comprehend
- [ ] Amazon Comprehend Medical
- [ ] Amazon DevOps Guru
- [ ] Amazon Fraud Detector
- [ ] AWS HealthLake
- [ ] Amazon Kendra
- [ ] Amazon Lex
- [ ] Amazon Lookout for Equipment
- [ ] Amazon Lookout for Metrics
- [ ] Amazon Lookout for Vision
- [ ] Amazon Mechanical Turk
- [ ] Amazon Personalize
- [ ] Amazon Polly
- [ ] Amazon Q
- [ ] Amazon Rekognition
- [ ] Amazon SageMaker
- [ ] Amazon Textract
- [ ] Amazon Transcribe
- [ ] Amazon Translate

### Management and Governance

- [ ] AWS Auto Scaling
- [ ] AWS Chatbot
- [ ] AWS CloudFormation
- [ ] AWS CloudTrail
- [ ] Amazon CloudWatch
- [ ] Amazon CloudWatch Logs
- [ ] AWS Compute Optimizer
- [ ] AWS Config
- [ ] AWS Organizations
- [ ] AWS Service Catalog
- [ ] AWS Systems Manager
- [ ] AWS Trusted Advisor

### Media

- [ ] Amazon Kinesis Video Streams

### Migration and Transfer

- [ ] AWS DataSync

### Networking and Content Delivery

- [ ] Amazon API Gateway
- [ ] Amazon CloudFront
- [ ] AWS Direct Connect
- [ ] Amazon VPC

### Security, Identity, and Compliance

- [ ] AWS IAM
- [ ] AWS KMS
- [ ] Amazon Macie
- [ ] AWS Secrets Manager

### Storage

- [ ] Amazon EBS
- [ ] Amazon EFS
- [ ] Amazon FSx
- [ ] Amazon S3
- [ ] Amazon S3 Glacier
- [ ] AWS Storage Gateway

## Domain 1: Data Preparation for ML (28%)

### Task 1.1: Ingest and store data

- [ ] Data formats: Parquet, JSON, CSV, ORC, Avro, RecordIO
- [ ] Core data sources: S3, EFS, FSx for NetApp ONTAP
- [ ] Streaming: Kinesis, Apache Flink, Apache Kafka
- [ ] SageMaker Data Wrangler, SageMaker Feature Store
- [ ] Merging data: AWS Glue, Apache Spark
- [ ] S3 Transfer Acceleration, EBS Provisioned IOPS
- [ ] Storage decisions: cost, performance, data structure

### Task 1.2: Transform data and feature engineering

- [ ] Cleaning: outliers, missing data, deduplication
- [ ] Feature engineering: scaling, standardization, binning, log transform, normalization
- [ ] Encoding: one-hot, binary, label encoding, tokenization
- [ ] Tools: SageMaker Data Wrangler, Glue, Glue DataBrew, Spark on EMR
- [ ] SageMaker Feature Store for managing features
- [ ] SageMaker Ground Truth, Mechanical Turk for labeling
- [ ] Lambda, Spark for streaming transforms

### Task 1.3: Ensure data integrity and prepare for modeling

- [ ] Pre-training bias metrics: class imbalance, difference in proportions of labels
- [ ] Strategies: synthetic data, resampling
- [ ] Data encryption, classification, anonymization, masking
- [ ] Compliance: PII, PHI, data residency
- [ ] Data quality: DataBrew, Glue Data Quality
- [ ] Bias detection: SageMaker Clarify
- [ ] Dataset splitting, shuffling, augmentation
- [ ] Loading data: EFS, FSx

## Domain 2: ML Model Development (26%)

### Task 2.1: Choose a modeling approach

- [ ] ML algorithms and business problem matching
- [ ] AWS AI services: Translate, Transcribe, Rekognition, Bedrock
- [ ] Interpretability in model selection
- [ ] SageMaker built-in algorithms
- [ ] SageMaker JumpStart, Amazon Bedrock for foundation models
- [ ] Model selection based on cost

### Task 2.2: Train and refine models

- [ ] Training elements: epoch, steps, batch size
- [ ] Reducing training time: early stopping, distributed training
- [ ] Regularization: dropout, weight decay, L1, L2
- [ ] Hyperparameter tuning: random search, Bayesian optimization
- [ ] SageMaker script mode: TensorFlow, PyTorch
- [ ] Fine-tuning pre-trained models: Bedrock, JumpStart
- [ ] SageMaker automatic model tuning (AMT)
- [ ] Overfitting, underfitting, catastrophic forgetting
- [ ] Ensembling, stacking, boosting
- [ ] Model compression: pruning, data type changes, feature selection
- [ ] SageMaker Model Registry for versioning

### Task 2.3: Analyze model performance

- [ ] Metrics: confusion matrix, F1, accuracy, precision, recall, RMSE, ROC, AUC
- [ ] Performance baselines
- [ ] Overfitting and underfitting detection
- [ ] SageMaker Clarify for model interpretability
- [ ] Convergence issues
- [ ] Shadow variant vs production variant
- [ ] SageMaker Model Debugger
- [ ] Tradeoffs: performance vs training time vs cost

## Domain 3: Deployment and Orchestration (22%)

### Task 3.1: Select deployment infrastructure

- [ ] Versioning, rollback strategies
- [ ] Real-time vs batch inference
- [ ] CPU vs GPU provisioning
- [ ] Endpoint types: serverless, real-time, asynchronous, batch
- [ ] Containers: provided or custom
- [ ] SageMaker Neo for edge optimization
- [ ] Multi-model and multi-container deployments
- [ ] Deployment targets: SageMaker endpoints, Kubernetes, ECS, EKS, Lambda
- [ ] Orchestrators: Apache Airflow, SageMaker Pipelines

### Task 3.2: Create and script infrastructure

- [ ] On-demand vs provisioned resources
- [ ] Scaling policies
- [ ] IaC: CloudFormation, AWS CDK
- [ ] Containerization: ECR, EKS, ECS, BYOC with SageMaker
- [ ] SageMaker endpoint auto scaling
- [ ] Spot Instances, EC2, Lambda behind endpoints
- [ ] SageMaker endpoints within VPC
- [ ] SageMaker SDK for deployment
- [ ] Auto scaling metrics: latency, CPU utilization, invocations per instance

### Task 3.3: CI/CD pipelines for ML

- [ ] CodePipeline, CodeBuild, CodeDeploy
- [ ] Git, version control
- [ ] CI/CD principles for ML workflows
- [ ] Deployment strategies: blue/green, canary, linear
- [ ] Gitflow, GitHub Flow
- [ ] SageMaker Pipelines, EventBridge for automation
- [ ] Automated tests: integration, unit, end-to-end
- [ ] Automated retraining mechanisms

## Domain 4: Monitoring, Maintenance, Security (24%)

### Task 4.1: Monitor model inference

- [ ] Model drift
- [ ] Data quality monitoring
- [ ] SageMaker Model Monitor
- [ ] SageMaker Clarify for distribution changes
- [ ] A/B testing in production

### Task 4.2: Monitor and optimize infrastructure and costs

- [ ] Metrics: utilization, throughput, availability, scalability, fault tolerance
- [ ] X-Ray, CloudWatch Lambda Insights, CloudWatch Logs Insights
- [ ] CloudTrail for logging and re-training triggers
- [ ] Instance types: memory optimized, compute optimized, general purpose, inference optimized
- [ ] Cost Explorer, Billing, Trusted Advisor
- [ ] Resource tagging for cost tracking
- [ ] CloudWatch alarms, dashboards
- [ ] QuickSight for dashboards
- [ ] EventBridge for monitoring events
- [ ] SageMaker Inference Recommender, Compute Optimizer for rightsizing
- [ ] Purchasing: Spot, On-Demand, Reserved, SageMaker Savings Plans

### Task 4.3: Secure AWS resources

- [ ] IAM roles, policies, groups
- [ ] Bucket policies, SageMaker Role Manager
- [ ] Network access controls for ML resources
- [ ] Security for CI/CD pipelines
- [ ] Least privilege access to ML artifacts
- [ ] VPCs, subnets, security groups for ML isolation
- [ ] Auditing and logging for compliance
