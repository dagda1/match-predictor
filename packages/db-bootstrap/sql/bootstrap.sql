DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'match_predictor_migrator') THEN
    CREATE USER match_predictor_migrator;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'match_predictor_app') THEN
    CREATE USER match_predictor_app;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'mlflow_migrator') THEN
    CREATE USER mlflow_migrator;
  END IF;
END
$$;

GRANT match_predictor_migrator TO CURRENT_USER;
GRANT match_predictor_app TO CURRENT_USER;
GRANT mlflow_migrator TO CURRENT_USER;

GRANT CREATE, USAGE ON SCHEMA public TO match_predictor_migrator;
GRANT ALL ON ALL TABLES IN SCHEMA public TO match_predictor_migrator;

GRANT USAGE ON SCHEMA public TO match_predictor_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO match_predictor_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO match_predictor_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO match_predictor_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO match_predictor_app;

ALTER DEFAULT PRIVILEGES FOR ROLE match_predictor_migrator IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO match_predictor_app;
ALTER DEFAULT PRIVILEGES FOR ROLE match_predictor_migrator IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO match_predictor_app;

ALTER ROLE mlflow_migrator CREATEDB;
GRANT rds_iam TO mlflow_migrator;
