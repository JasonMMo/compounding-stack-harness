---
generated: 2026-06-18
author: DBA-agent
scope: legal-rag-mvp schema (Growth-48)
---

# ERD — legal-rag-mvp

## Entity Relationship Diagram (Mermaid)

```mermaid
erDiagram
    legal_case {
        uuid id PK
        string case_number UK
        string title
        enum case_type
        enum status
        date filed_date
        string court
        date next_hearing_date
        uuid assigned_attorney_id FK
        uuid partner_id
        uuid client_contact_id FK
        text summary
        tsvector fts_vector
        timestamptz created_at
        timestamptz updated_at
    }

    legal_case_party {
        uuid id PK
        uuid case_id FK
        enum role
        string name
        uuid contact_id FK
        string notes
        timestamptz created_at
        timestamptz updated_at
    }

    legal_case_document {
        uuid id PK
        uuid case_id FK
        enum document_type
        string title
        timestamptz filed_at
        string storage_key
        text content_text
        tsvector fts_vector
        string ingest_status
        timestamptz ingested_at
        string notes
        timestamptz created_at
        timestamptz updated_at
    }

    legal_precedent {
        uuid id PK
        string citation UK
        string court
        date decided_date
        enum case_type
        text holding
        text full_text
        string keywords
        tsvector fts_vector
        vector_768 holding_embedding
        timestamptz embedded_at
        timestamptz created_at
        timestamptz updated_at
    }

    legal_document_chunk {
        uuid id PK
        string source_type
        uuid source_id
        uuid case_id FK
        integer chunk_index
        text chunk_text
        integer token_count
        vector_768 embedding
        timestamptz embedded_at
        string model_version
        timestamptz created_at
        timestamptz updated_at
    }

    legal_rag_query_log {
        uuid id PK
        uuid attorney_id
        uuid case_id FK
        text query_text
        vector_768 query_embedding
        text retrieved_chunk_ids
        text citations_summary
        text answer_text
        string model_id
        integer tokens_used
        integer latency_ms
        string status
        text error_message
        timestamptz created_at
        timestamptz updated_at
    }

    legal_case         ||--o{ legal_case_party       : "has parties"
    legal_case         ||--o{ legal_case_document     : "has documents"
    legal_case         ||--o{ legal_document_chunk    : "chunks scoped to case"
    legal_case         ||--o{ legal_rag_query_log     : "query history"
    legal_case_document||--o{ legal_document_chunk    : "chunked into"
    legal_precedent    ||--o{ legal_document_chunk    : "chunked into"
```

## Cardinality Notes

| Relationship | Type | Note |
|---|---|---|
| legal_case → legal_case_party | 1:N | Multiple parties per case |
| legal_case → legal_case_document | 1:N | Append-only audit trail |
| legal_case_document → legal_document_chunk | 1:N | Ingest creates N chunks per doc |
| legal_precedent → legal_document_chunk | 1:N | Full-text chunked for RAG |
| legal_document_chunk (source_type='precedent') | polymorphic | source_id → legal_precedent.id |
| legal_document_chunk (source_type='case_document') | polymorphic | source_id → legal_case_document.id |
| legal_rag_query_log → legal_document_chunk | M:N logical | via retrieved_chunk_ids (JSON array) |

## Citation Chain (anti-hallucination path)

```
RAG answer
  └── references chunk_ids from legal_rag_query_log.retrieved_chunk_ids
        └── legal_document_chunk.id
              ├── source_type='precedent'    → legal_precedent.citation  (human-readable cite)
              └── source_type='case_document' → legal_case_document.id + title
```

Every cited source traces to a DB PK. Engineer must validate: answer citations
must be a subset of `retrieved_chunk_ids` in the same query log row.
