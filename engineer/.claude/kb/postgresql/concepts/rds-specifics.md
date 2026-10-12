# Amazon RDS for PostgreSQL Specifics

> **Purpose**: Versions, encryption, TLS, parameter groups, backups/PITR, and connection budgeting on RDS
> **Confidence**: 0.90
> **MCP Validated**: 2026-10-02

## Overview

RDS offers PostgreSQL 18 (18.6) as GA alongside 17, 16, 15 (PostgreSQL 19 beta is preview only).
Upstream 14 reaches end of community support 2026-11-12. If you specify only a major version,
RDS picks a recent minor; list the preferred one with
`aws rds describe-db-engine-versions --default-only --engine postgres`.

## Quick Reference

| Topic | Facts |
|-------|-------|
| Encryption at rest | AES-256 via AWS KMS; covers storage, logs, automated backups, replicas, snapshots |
| Enabling | Only at creation (`--storage-encrypted`, optional `--kms-key-id`); cannot be disabled |
| Encrypt existing | Snapshot, copy snapshot with encryption + KMS key, restore from the copy |
| KMS key | Cannot change on an existing instance; replicas in same Region use same key; disabling the key makes the instance inaccessible (recoverable for 7 days by re-enabling and restarting) |
| TLS | `rds.force_ssl` defaults to 1 on PG 15+ (0 on 14 and older); libpq default `sslmode=prefer`; use `sslmode=verify-full` + `sslrootcert=<RDS CA bundle>`; TLS 1.3 on PG 16+ |
| Parameter groups | Default groups cannot be edited; create a custom group and associate it |
| Apply type | Static: `pending-reboot`, needs manual reboot. Dynamic: immediate (console always `immediate`). Newly associated group applies after reboot |
| Automated backups | Retention 0-35 days (0 disables; console default 7, CLI/API default 1); changing 0 <-> nonzero causes an outage |
| PITR | Transaction logs to S3 every 5 minutes; `LatestRestorableTime`; restore always creates a NEW instance (`restore-db-instance-to-point-in-time`) |
| After restore | Gets default parameter/option groups unless specified (CLI/API) or changed after (console); storage cannot shrink |
| Snapshots | Manual snapshots are kept after instance delete (limit 100/Region); automated backups are deleted with the instance unless retained |
| Autovacuum | On by default for new instances; AWS strongly recommends keeping it on (not running it can force an outage for a much more intrusive vacuum); its bulk-load guidance disables it only temporarily |
| DNS | Keep client DNS TTL under 30 seconds; IP changes on failover; test failover |

## Connection budget

```text
max_connections (instance) >= sum over app processes of (pool_size + max_overflow)
                              + procrastinate workers (pool max_size + 1 LISTEN connection each)
                              + migrations/admin headroom
```

Procrastinate: each worker uses one extra connection for LISTEN/NOTIFY; disable with
`listen_notify=False` / `--no-listen-notify` when connections are scarce (documented). Practitioner
note: LISTEN also needs a session-level connection, so avoid it behind transaction-pooling proxies.

## Common Mistakes

### Wrong

```text
Restoring "in place" over the production instance (PITR cannot do this)
Editing the default parameter group
```

### Correct

```text
PITR -> new instance -> validate -> repoint the application (or copy data back)
Create custom parameter group, associate it, reboot if the parameter is static
```

## Related

- [aws KB](../../aws/index.md), [terraform KB](../../terraform/index.md)
- [SQLAlchemy engine/session](sqlalchemy-engine-session.md)
- [Procrastinate tasks and workers](../patterns/procrastinate-tasks-and-workers.md)

## Sources

- https://www.postgresql.org/support/versioning/
- https://docs.aws.amazon.com/AmazonRDS/latest/PostgreSQLReleaseNotes/postgresql-versions.html
- https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.Encryption.html
- https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/PostgreSQL.Concepts.General.SSL.html
- https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/parameter-groups-overview.html
- https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.BackupRetention.html
- https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIT.html
- https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html
- https://procrastinate.readthedocs.io/en/stable/howto/production/connections.html
