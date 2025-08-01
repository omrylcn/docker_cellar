-- Initialize ML Analytics Database
-- This script runs automatically when PostgreSQL starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS ml_models;
CREATE SCHEMA IF NOT EXISTS ml_experiments;
CREATE SCHEMA IF NOT EXISTS ml_analytics;

-- Create users table
CREATE TABLE IF NOT EXISTS ml_analytics.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create model registry table
CREATE TABLE IF NOT EXISTS ml_models.model_registry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- 'classification', 'regression', 'clustering'
    framework VARCHAR(50) NOT NULL, -- 'sklearn', 'pytorch', 'tensorflow', 'onnx'
    file_path TEXT NOT NULL,
    metadata JSONB,
    performance_metrics JSONB,
    created_by UUID REFERENCES ml_analytics.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(model_name, model_version)
);

-- Create experiments table
CREATE TABLE IF NOT EXISTS ml_experiments.experiments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_name VARCHAR(100) NOT NULL,
    description TEXT,
    model_id UUID REFERENCES ml_models.model_registry(id),
    parameters JSONB,
    metrics JSONB,
    status VARCHAR(20) DEFAULT 'running', -- 'running', 'completed', 'failed'
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES ml_analytics.users(id)
);

-- Create predictions table for logging
CREATE TABLE IF NOT EXISTS ml_analytics.predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES ml_models.model_registry(id),
    input_data JSONB NOT NULL,
    prediction_result JSONB NOT NULL,
    confidence_score FLOAT,
    prediction_time_ms FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id UUID REFERENCES ml_analytics.users(id),
    session_id VARCHAR(100),
    api_version VARCHAR(20)
);

-- Create model performance table
CREATE TABLE IF NOT EXISTS ml_analytics.model_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES ml_models.model_registry(id),
    metric_name VARCHAR(50) NOT NULL,
    metric_value FLOAT NOT NULL,
    evaluation_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    dataset_info JSONB,
    created_by UUID REFERENCES ml_analytics.users(id)
);

-- Create feature store table
CREATE TABLE IF NOT EXISTS ml_analytics.feature_store (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feature_name VARCHAR(100) NOT NULL,
    feature_type VARCHAR(50) NOT NULL, -- 'numerical', 'categorical', 'text', 'image'
    description TEXT,
    source_table VARCHAR(100),
    transformation_logic TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_predictions_model_id ON ml_analytics.predictions(model_id);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON ml_analytics.predictions(created_at);
CREATE INDEX IF NOT EXISTS idx_predictions_user_id ON ml_analytics.predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_experiments_model_id ON ml_experiments.experiments(model_id);
CREATE INDEX IF NOT EXISTS idx_experiments_status ON ml_experiments.experiments(status);
CREATE INDEX IF NOT EXISTS idx_model_registry_name_version ON ml_models.model_registry(model_name, model_version);
CREATE INDEX IF NOT EXISTS idx_model_performance_model_id ON ml_analytics.model_performance(model_id);

-- Insert sample data
INSERT INTO ml_analytics.users (username, email) 
VALUES 
    ('admin', 'admin@mlanalytics.com'),
    ('data_scientist', 'ds@mlanalytics.com'),
    ('ml_engineer', 'mle@mlanalytics.com')
ON CONFLICT (username) DO NOTHING;

-- Insert sample model
INSERT INTO ml_models.model_registry (
    model_name, 
    model_version, 
    model_type, 
    framework, 
    file_path, 
    metadata,
    performance_metrics,
    created_by
) 
SELECT 
    'random_forest_classifier',
    '1.0.0',
    'classification',
    'onnx',
    '/models/random_forest_classifier.onnx',
    '{"input_features": 10, "output_classes": 3, "training_samples": 1000}'::jsonb,
    '{"accuracy": 0.867, "precision": 0.871, "recall": 0.863, "f1_score": 0.867}'::jsonb,
    u.id
FROM ml_analytics.users u 
WHERE u.username = 'admin'
ON CONFLICT (model_name, model_version) DO NOTHING;

-- Insert sample features
INSERT INTO ml_analytics.feature_store (feature_name, feature_type, description)
VALUES 
    ('feature_0', 'numerical', 'First numerical feature'),
    ('feature_1', 'numerical', 'Second numerical feature'),
    ('feature_2', 'numerical', 'Third numerical feature'),
    ('feature_3', 'numerical', 'Fourth numerical feature'),
    ('feature_4', 'numerical', 'Fifth numerical feature'),
    ('feature_5', 'numerical', 'Sixth numerical feature'),
    ('feature_6', 'numerical', 'Seventh numerical feature'),
    ('feature_7', 'numerical', 'Eighth numerical feature'),
    ('feature_8', 'numerical', 'Ninth numerical feature'),
    ('feature_9', 'numerical', 'Tenth numerical feature')
ON CONFLICT DO NOTHING;

-- Create views for analytics
CREATE OR REPLACE VIEW ml_analytics.daily_predictions AS
SELECT 
    DATE(created_at) AS prediction_date,
    model_id,
    COUNT(*) AS total_predictions,
    AVG(prediction_time_ms) AS avg_prediction_time,
    AVG(confidence_score) AS avg_confidence
FROM ml_analytics.predictions
GROUP BY DATE(created_at), model_id
ORDER BY prediction_date DESC;

CREATE OR REPLACE VIEW ml_analytics.model_performance_summary AS
SELECT 
    mr.model_name,
    mr.model_version,
    mr.model_type,
    mr.framework,
    COUNT(p.id) AS total_predictions,
    AVG(p.prediction_time_ms) AS avg_prediction_time,
    mr.performance_metrics,
    mr.created_at AS model_created_at
FROM ml_models.model_registry mr
LEFT JOIN ml_analytics.predictions p ON mr.id = p.model_id
WHERE mr.is_active = TRUE
GROUP BY mr.id, mr.model_name, mr.model_version, mr.model_type, mr.framework, mr.performance_metrics, mr.created_at
ORDER BY mr.created_at DESC;

-- Grant permissions
GRANT USAGE ON SCHEMA ml_models TO PUBLIC;
GRANT USAGE ON SCHEMA ml_experiments TO PUBLIC;
GRANT USAGE ON SCHEMA ml_analytics TO PUBLIC;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ml_models TO PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ml_experiments TO PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ml_analytics TO PUBLIC;

GRANT SELECT ON ALL VIEWS IN SCHEMA ml_analytics TO PUBLIC;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ml_models TO PUBLIC;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ml_experiments TO PUBLIC;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ml_analytics TO PUBLIC;