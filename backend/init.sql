-- Enable pgvector extension for AI embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a simple health check function
CREATE OR REPLACE FUNCTION health_check() RETURNS TEXT AS $$
BEGIN
    RETURN 'MTCloud Database Ready';
END;
$$ LANGUAGE plpgsql;
