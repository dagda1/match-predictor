# AWS MLA-C01 — Machine Learning Engineer Associate

Source: https://docs.aws.amazon.com/aws-certification/latest/examguides/machine-learning-engineer-associate-01.html

Exam: $150, 65 questions, 130 minutes, pass 720/1000

## Context for agents

- Paul is a frontend dev pivoting to MLOps
- He knows: programming (not Python), Docker, Terraform, CI/CD, Linux
- He does NOT know: Python syntax, AWS ML services, ML theory beyond basics
- He learns by doing, not videos or books
- Each service checkbox gets sub-tasks tied to this repo (match-predictor)
- Infrastructure inside this repo (match-predictor) must be CDK or CloudFormation — no web console, no Terraform
- Hands-on work in other Paul-owned repos counts toward a checkbox even if it uses Terraform, provided it deploys the actual AWS service and a sub-bullet links to the plan / repo
- Do NOT generate code for him — answer questions, check his work, explain errors
- Do NOT make assumptions or state things as fact without a source
- Do NOT write walls of text
- Checked boxes = done. Work top to bottom. Resume from the first unchecked item.

## In-scope AWS services

Source: https://docs.aws.amazon.com/aws-certification/latest/examguides/mla-01-in-scope-services.html

### commands
  - `aws iam list-roles --query "Roles[?starts_with(CreateDate, '2026-03-07')].[RoleName, Arn]" --output table`

### Analytics

- [X] Amazon Athena
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
  - [X] Automate daily ETL (replaces manual scraper runs):
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
  - [X] Move API data to Postgres (RDS):
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
    - [X] Put Lambdas in VPC — `vpc`, `vpc_subnets`, `security_groups` on Lambdas in `functions.py` and `api.py`
    - [X] Lambdas use IPv6 dual-stack — `ipv6_allowed_for_dual_stack=True`
    - [X] S3 gateway VPC endpoint + endpoint policy scoped to data bucket — `vpc.py`, `deploy_stack.py`
    - [X] RDS has `iam_authentication=True` — `database.py`
    - [X] Bootstrap Lambda custom resource — `packages/db-bootstrap/`, `deploy_stack/bootstrap.py`
      - Runs once as master user
      - Creates `match_predictor_migrator` and `match_predictor_app` users
      - Grants `rds_iam` to both (password auth disabled on these users)
      - Master user used only for bootstrap, never at runtime
    - [X] IAM auth for Lambda → RDS:
      - [X] Grant `rds-db:connect` on migrator user ARN to migration Lambda role
      - [X] Grant `rds-db:connect` on app user ARN to API + predictor + scraper Lambda roles
      - [X] Lambda code uses `generate_db_auth_token()` to mint token, passes as Postgres password
    - [X] Migration Lambda — runs `alembic upgrade head` as `match_predictor_migrator`
      - Separate lean Docker image (alembic, sqlalchemy, psycopg2-binary)
      - Custom resource triggered each deploy (Version = hash of alembic versions dir)
    - [X] Pass `DB_HOST` / `DB_USER` / `DB_NAME` / `DB_REGION` env vars to API + predictor + scraper Lambdas
      - Diverged from `DATABASE_URL`: API uses shared `create_db_engine()` from ml package — falls through to env-var + IAM token in AWS, supports `DATABASE_URL` only for local dev via `.env`
    - [X] Predictor Lambda writes to Postgres instead of S3 JSON files (predictions, upcoming, team_features)
    - [X] Seed step — `InitialDataLoad` AwsCustomResource invokes scraper async on stack create; scraper writes matches → SQS → predictor populates the rest
    - [X] API Lambda reads from Postgres in AWS
    - [X] Model file moved to **EFS** (diverged from "stays in S3"): new `ModelStorage` construct mounts `/mnt/model` on predictor + API; predictor writes the joblib there, API reads it via `MODEL_PATH` env var
    - [X] Remove S3 JSON file reading from API
    - [X] `psycopg2-binary` + `sqlalchemy` already in API's dep chain via `match-predictor-ml`
    - [X] RDS CA bundle baked into all Python Lambda images via `assets/rds-ca-bundle.pem` + Dockerfile COPYs; `sslmode=verify-full` everywhere; etl scraper bundles the same bundle via CDK `IncludeRdsCaBundle` command hook
    - [X] Lambda SG allows IPv6 egress (`allow_all_ipv6_outbound=True`) — without this, IPv6 packets to AWS service public endpoints hung at the SG layer, causing `get_secret_value` to time out
    - [X] EventBridge keep-warm rule pings API Lambda every 5 minutes with `{"source": "lambda.warmup"}`; handler short-circuits before Mangum to keep the container hot
- [X] Amazon Data Firehose — CloudWatch Logs subscription filter on API Lambda log group → Firehose delivery stream → S3 (`logs/` prefix, GZIP). Transform Lambda (NodejsFunction) decompresses each CloudWatch envelope and emits one NDJSON line per `logEvent` with `{timestamp, message, logGroup, logStream}`.
- [ ] Amazon EMR
- [X] AWS Glue — `LogsDatabase` + `LogsTable` over the `logs/` S3 prefix using `org.openx.data.jsonserde.JsonSerDe`. Column-to-JSON-key mapping handles camelCase keys (`logGroup` → `log_group`, `timestamp` → `event_time`). Athena queries against `logs.logs` confirmed working.
- [ ] AWS Glue DataBrew
- [ ] AWS Glue Data Quality
- [ ] Amazon Kinesis
- [ ] AWS Lake Formation
- [ ] Amazon Managed Service for Apache Flink
- [ ] Amazon OpenSearch Service
- [ ] Amazon QuickSight
- [ ] Amazon Redshift

### Application Integration

- [X] Amazon EventBridge (covered by daily ETL + keep-warm rule)
- [ ] Amazon MWAA (Managed Workflows for Apache Airflow)
- [X] Amazon SNS (alerts construct)
- [X] Amazon SQS (scraper → predictor queue)
- [ ] AWS Step Functions

### Cloud Financial Management

- [ ] AWS Billing and Cost Management
- [ ] AWS Budgets
- [ ] AWS Cost Explorer

### Compute

- [ ] AWS Batch
- [ ] Amazon EC2
- [X] AWS Lambda (scraper, predictor, API, bootstrap, migration; container + zip; VPC + EFS)
- [ ] AWS Serverless Application Repository

### Containers

- [X] Amazon ECR (CDK auto-publishes container images for predictor / migration / API)
- [X] Amazon ECS
  - cuttingedge `apps/frontendsupport` live on Fargate (Terraform, in the cuttingedge repo).
  - cuttingedge `apps/website` live on Fargate behind ALB + CloudFront, deployed via **CDK** in this repo (`packages/deploy/deploy/website_stack/`): Network + Alb + Ecs + Cdn constructs, cluster/service `website`, image from ECR `website_server`. Serving `https://cutting.scot` (us-east-1), migrated off a DigitalOcean droplet.
- [ ] Amazon EKS

### Database

- [ ] Amazon DocumentDB
- [ ] Amazon DynamoDB
- [ ] Amazon ElastiCache
- [ ] Amazon Neptune
- [X] Amazon RDS (Postgres in private subnets, IAM auth, TLS verify-full)

### Developer Tools

- [X] AWS CDK (entire stack)
- [ ] AWS CodeArtifact
- [ ] AWS CodeBuild
- [ ] AWS CodeDeploy
- [ ] AWS CodePipeline
- [X] AWS X-Ray (tracing on all Lambdas)

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
- [X] AWS CloudFormation (synthed by CDK)
- [ ] AWS CloudTrail
- [X] Amazon CloudWatch (alarms construct)
- [X] Amazon CloudWatch Logs (Lambda logs everywhere)
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

- [X] Amazon API Gateway (HTTP API in front of API Lambda)
- [X] Amazon CloudFront (frontend + API origin + WAF)
- [ ] AWS Direct Connect
- [X] Amazon VPC (dual-stack, public/private subnets, NAT, EIGW, S3 gateway endpoint)

### Security, Identity, and Compliance

- [X] AWS IAM (OIDC trust for GitHub Actions, per-Lambda execution roles, scoped policies)
- [ ] AWS KMS
- [ ] Amazon Macie
- [X] AWS Secrets Manager (RDS master credentials, CloudFront origin verify token)

### Storage

- [ ] Amazon EBS
- [X] Amazon EFS (model storage shared between predictor and API via access point)
- [ ] Amazon FSx
- [X] Amazon S3 (frontend bucket, data bucket, access logs)
- [ ] Amazon S3 Glacier
- [ ] AWS Storage Gateway

## Domain 1: Data Preparation for ML (28%)

### Task 1.1: Ingest and store data

- [X] Data formats: Parquet, JSON, CSV, ORC, Avro, RecordIO — used JSON (S3) and now Postgres rows
- [X] Core data sources: S3, EFS, FSx for NetApp ONTAP — using S3 (data + frontend) and EFS (model)
- [ ] Streaming: Kinesis, Apache Flink, Apache Kafka
- [ ] SageMaker Data Wrangler, SageMaker Feature Store
- [ ] Merging data: AWS Glue, Apache Spark
- [ ] S3 Transfer Acceleration, EBS Provisioned IOPS
- [X] Storage decisions: cost, performance, data structure — picked Postgres over S3 JSON for query needs, EFS over S3 for model file

### Task 1.2: Transform data and feature engineering

- [X] Cleaning: outliers, missing data, deduplication — `ON CONFLICT (id) DO UPDATE` on matches insert; Zod validation rejects malformed rows at scraper boundary
- [X] Feature engineering: scaling, standardization, binning, log transform, normalization — rolling averages over last 5 matches per team in `features.py`
- [ ] Encoding: one-hot, binary, label encoding, tokenization
- [ ] Tools: SageMaker Data Wrangler, Glue, Glue DataBrew, Spark on EMR
- [ ] SageMaker Feature Store for managing features — `team_features` table is our hand-rolled equivalent
- [ ] SageMaker Ground Truth, Mechanical Turk for labeling
- [X] Lambda, Spark for streaming transforms — Lambda for the scrape → transform → DB pipeline

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

- [X] ML algorithms and business problem matching — GradientBoostingClassifier for 3-class outcome, Poisson for goal counts
- [ ] AWS AI services: Translate, Transcribe, Rekognition, Bedrock
- [X] Interpretability in model selection — model returns probabilities + scoreline distributions, not just predicted class
- [ ] SageMaker built-in algorithms
- [ ] SageMaker JumpStart, Amazon Bedrock for foundation models
- [X] Model selection based on cost — sklearn on Lambda chosen over SageMaker endpoints to keep idle cost at $0

### Task 2.2: Train and refine models

- [X] Training elements: epoch, steps, batch size — sklearn equivalents: `n_estimators=200`, `max_depth=4`, `learning_rate=0.1`
- [ ] Reducing training time: early stopping, distributed training
- [ ] Regularization: dropout, weight decay, L1, L2
- [ ] Hyperparameter tuning: random search, Bayesian optimization
- [ ] SageMaker script mode: TensorFlow, PyTorch
- [ ] Fine-tuning pre-trained models: Bedrock, JumpStart
- [ ] SageMaker automatic model tuning (AMT)
- [X] Overfitting, underfitting, catastrophic forgetting — 5-fold TimeSeriesSplit cross-validation prevents leakage; features only use pre-match data
- [X] Ensembling, stacking, boosting — gradient boosting (sklearn GradientBoostingClassifier)
- [ ] Model compression: pruning, data type changes, feature selection
- [ ] SageMaker Model Registry for versioning

### Task 2.3: Analyze model performance

- [X] Metrics: confusion matrix, F1, accuracy, precision, recall, RMSE, ROC, AUC — accuracy tracked per-prediction in `predictions.ml_correct` / `poisson_correct`, surfaced on `/results`
- [X] Performance baselines — Poisson model is the explicit baseline ML must beat
- [X] Overfitting and underfitting detection — TimeSeriesSplit holds out future games during training
- [ ] SageMaker Clarify for model interpretability
- [ ] Convergence issues
- [ ] Shadow variant vs production variant — both ML and Poisson predictions stored side-by-side, comparable per match
- [ ] SageMaker Model Debugger
- [X] Tradeoffs: performance vs training time vs cost — sklearn on Lambda picked for cost; training fits inside the predictor Lambda's 15-min budget

## Domain 3: Deployment and Orchestration (22%)

### Task 3.1: Select deployment infrastructure

- [ ] Versioning, rollback strategies
- [X] Real-time vs batch inference — `/predict` is real-time, scheduled batch run computes historical predictions and `team_features`
- [X] CPU vs GPU provisioning — CPU (Lambda has no GPU; sklearn doesn't need one)
- [X] Endpoint types: serverless, real-time, asynchronous, batch — Lambda serverless real-time for `/predict`; EventBridge-scheduled batch for the daily run
- [X] Containers: provided or custom — custom container images (Python 3.13 base) for predictor, migration, API
- [ ] SageMaker Neo for edge optimization
- [ ] Multi-model and multi-container deployments
- [X] Deployment targets: SageMaker endpoints, Kubernetes, ECS, EKS, Lambda — Lambda
- [X] Orchestrators: Apache Airflow, SageMaker Pipelines — EventBridge + SQS chain (scraper → predictor) acts as a tiny orchestrator

### Task 3.2: Create and script infrastructure

- [X] On-demand vs provisioned resources — Lambda on-demand, considered Provisioned Concurrency for cold starts
- [ ] Scaling policies
- [X] IaC: CloudFormation, AWS CDK — entire stack in CDK Python
- [X] Containerization: ECR, EKS, ECS, BYOC with SageMaker — ECR for predictor / migration / API images
- [ ] SageMaker endpoint auto scaling
- [X] Spot Instances, EC2, Lambda behind endpoints — Lambda behind API Gateway behind CloudFront
- [ ] SageMaker endpoints within VPC
- [ ] SageMaker SDK for deployment
- [ ] Auto scaling metrics: latency, CPU utilization, invocations per instance

### Task 3.3: CI/CD pipelines for ML

- [ ] CodePipeline, CodeBuild, CodeDeploy
- [X] Git, version control
- [X] CI/CD principles for ML workflows — GitHub Actions OIDC → cdk deploy on every push
- [ ] Deployment strategies: blue/green, canary, linear
- [X] Gitflow, GitHub Flow
- [X] SageMaker Pipelines, EventBridge for automation — EventBridge daily scrape + 5-min keep-warm
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
- [X] X-Ray, CloudWatch Lambda Insights, CloudWatch Logs Insights — X-Ray active on all Lambdas, Lambda logs to CloudWatch
- [ ] CloudTrail for logging and re-training triggers
- [ ] Instance types: memory optimized, compute optimized, general purpose, inference optimized
- [ ] Cost Explorer, Billing, Trusted Advisor
- [ ] Resource tagging for cost tracking
- [X] CloudWatch alarms, dashboards — alarms in `alerts.py`
- [ ] QuickSight for dashboards
- [X] EventBridge for monitoring events — daily scrape + 5-min keep-warm
- [ ] SageMaker Inference Recommender, Compute Optimizer for rightsizing
- [ ] Purchasing: Spot, On-Demand, Reserved, SageMaker Savings Plans

### Task 4.3: Secure AWS resources

- [X] IAM roles, policies, groups — per-Lambda execution roles, scoped policies (`rds-db:connect` on specific user ARN, `grant_read` on specific bucket/secret), no wildcards
- [X] Bucket policies — data bucket: block-public-access, enforce-SSL, server access logs, lifecycle rules; frontend bucket fronted by CloudFront OAC
- [X] Network access controls for ML resources — three SGs (Lambda, Database, EFS) with port-specific ingress (5432 only Lambda→DB, 2049 only Lambda→EFS)
- [X] Security for CI/CD pipelines — GitHub OIDC trust, scoped deploy role
- [X] Least privilege access to ML artifacts — bootstrap creates `migrator` (DDL only) + `app` (DML only) DB users; model on EFS, predictor writes / API reads
- [X] VPCs, subnets, security groups for ML isolation — dual-stack VPC, public/private subnets, Lambdas in private subnets only
- [ ] Auditing and logging for compliance — CloudWatch Lambda logs exist, but no CloudTrail enabled, no Config rules, no compliance dashboards
