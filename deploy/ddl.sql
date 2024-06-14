CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS whatap_docs_temp (id uuid PRIMARY KEY, metadata jsonb, embedding vector(1536));
CREATE OR REPLACE function match_whatap_docs_temp (
    query_embedding vector(1536),
    similarity_threshold float,
    match_count int
  )
  returns TABLE (id uuid, metadata jsonb, similarity float)
  LANGUAGE plpgsql
  AS $$
  BEGIN
    return query
    SELECT whatap_docs_temp.id, whatap_docs_temp.metadata, 1 - (whatap_docs_temp.embedding <=> query_embedding) AS similarity
    FROM whatap_docs_temp
    WHERE 1 - (whatap_docs_temp.embedding <=> query_embedding) > similarity_threshold
    ORDER BY whatap_docs_temp.embedding <=> query_embedding
    LIMIT match_count;
  END; $$

CREATE INDEX IF NOT EXISTS idx_l2_ops ON whatap_docs USING hnsw (embedding vector_l2_ops);
CREATE INDEX IF NOT EXISTS idx_ip_ops ON whatap_docs USING hnsw (embedding vector_ip_ops);
CREATE INDEX IF NOT EXISTS idx_cosine_ops ON whatap_docs USING hnsw (embedding vector_cosine_ops);
