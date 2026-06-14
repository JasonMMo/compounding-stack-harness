PII-free per-client case lifecycle snapshots, written by intake_sync.py (Phase 4) via
`audit.case_snapshot()`. Each file is named `<client_id>.yaml` where `client_id` is the
first 16 hex characters of SHA256(email) — never the email itself. Raw PII audit logs
(`audit.jsonl`, containing email and free-text answers) live only on the VPS under
`DATA_DIR/clients/<client_id>/` and in the gitignored local data-mirror
(`apps/intake/data-mirror/`); they are never committed to this repository.
