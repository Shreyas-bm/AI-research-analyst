# PostgreSQL pgvector vs ChromaDB Vector Database Benchmark (Internal Engineering Report)

## Executive Summary
This internal evaluation measures the query latency, indexing time, and memory overhead of `pgvector` (HNSW) versus `ChromaDB` (embedded SQLite/DuckDB + hnswlib) for workloads between 100,000 and 1,000,000 vector embeddings (1536 dimensions).

## Performance Comparison
1. **Query Latency (p95 at 50 QPS, 500k vectors)**:
   - `pgvector` HNSW (m=16, ef_construction=64): 12.4ms p95 latency.
   - `ChromaDB` (local embedded): 8.9ms p95 latency.
   - `ChromaDB` (client/server HTTP mode): 18.2ms p95 latency.

2. **Memory Footprint**:
   - `pgvector` shared buffers & work_mem: ~1.2 GB RAM for 500k embeddings.
   - `ChromaDB` in-process RAM: ~2.1 GB RAM for 500k embeddings.

3. **Operational Complexity**:
   - `pgvector`: Single ACID database. Zero dual-write sync issues. Existing backup tooling (pg_dump, WAL archiving) applies directly.
   - `ChromaDB`: Dedicated vector store. Requires dual-write synchronization with relational store (Postgres). Potential state divergence if worker crashes during write.

4. **Filtering Capabilities**:
   - `pgvector`: Native SQL WHERE filtering combined with vector indexes via iterative index scans.
   - `ChromaDB`: Metadata filtering on scalar fields in-memory before/after vector retrieval.

## Conclusion and Recommendations
For teams already running PostgreSQL with under 2,000,000 vectors and strict ACID requirements, `pgvector` eliminates architectural drift and reduces operational overhead to near zero. ChromaDB is recommended when decoupled vector storage or microservices isolation is required.
