# Route 53, RDS Basics, and When to Add Services

> **Purpose**: DNS records, RDS encryption/availability basics, and triggers for ALB/Fargate/SQS/CloudFront/WAF
> **Confidence**: 0.85 (service facts 0.95; "when worthwhile" thresholds are practitioner judgment)
> **MCP Validated**: 2026-10-02

## Route 53

| Topic | Fact |
|-------|------|
| Alias vs CNAME | alias works at the zone apex (example.com); CNAME cannot; alias queries to AWS resources are free; alias TTL cannot be set |
| Alias targets | CloudFront, ELB (ALB/NLB/CLB), API Gateway, S3 website, another record in the zone, and others |
| Instance without ELB | plain `A` record holding the server's IPv4 address (alias only targets supported AWS resources) |
| Migrating a live domain | create hosted zone, copy records, lower NS TTL (60-900 s recommended) on both providers, wait out the old TTL, then change NS at the registrar; remove the DS record first if DNSSEC is on |
| Hosted-zone housekeeping | do not add or delete the zone's NS/SOA records |
| SES tie-in | SES can publish DKIM/MAIL FROM records to Route 53 when you create the identity |

## RDS (high level)

| Topic | Fact |
|-------|------|
| Encryption at rest | AES-256 via KMS; includes storage, logs, backups, snapshots, replicas |
| When to enable | only at creation; cannot be disabled; encrypt an existing DB by copying a snapshot with encryption and restoring it |
| KMS key | cannot change on an existing instance; replicas in-Region use the same key; a disabled key makes the instance inaccessible |
| Encryption in transit | separate from at-rest (at-rest encryption does not cover client connections); configure TLS per engine |
| Multi-AZ instance | synchronous standby in another AZ, automatic failover; standby is not readable (use replicas for reads); higher write/commit latency |
| Backups | automated backups enable point-in-time restore within the retention period and are deleted with the instance unless retained; take a final snapshot; 100 manual snapshots per Region |
| Connections | many short-lived connections: use RDS Proxy |
| Quotas | 40 DB instances per Region default (adjustable) |

Not verified here: RDS availability in `sa-east-1`, backup retention maximum, failover duration.
Check the RDS console/regions page before committing.

## When to Add Services (practitioner guidance over AWS facts)

| Service | AWS-documented role | Add when |
|---------|---------------------|----------|
| Application Load Balancer | L7 routing (path/host/header rules), per-target-group health checks, ACM TLS termination, WAF, Cognito authentication | 2+ app instances or zero-downtime deploys; path-based routing to several services; need WAF or managed TLS |
| ECS Fargate | run containers without managing servers; per-task isolation; ALB target type `ip` | EC2 patching/capacity management becomes the bottleneck, or you need multiple replicas per service |
| SQS | durable queue; standard = at-least-once, FIFO = exactly-once processing; retention 60 s-14 days (default 4) | async work must survive restarts independent of the database, or producers outpace consumers; a Postgres-backed queue is adequate until then |
| CloudFront | edge caching; S3 or HTTP origins; signed URLs/cookies for private content | static assets/SPA served globally, or you want to keep the S3 bucket private behind a CDN |
| AWS WAF | web ACLs on CloudFront, ALB, API Gateway, Cognito user pools, others | public endpoints facing abuse (bots, injection, rate abuse) |

Order of likely adoption: ALB + ACM (TLS, health checks) before WAF (needs a supported
attachment point); CloudFront before Fargate if the problem is static delivery, not compute.
These thresholds are judgment calls, not AWS statements.

## Common Mistakes

### Wrong

```text
CNAME at the zone apex; encrypting RDS "later" with a flag flip.
```

### Correct

```text
Alias/A record at the apex; decide RDS encryption and KMS key before first create.
```

## Related

- [AWS ECS Fargate (data engineering domain)](../../aws/containers/concepts/ecs-fargate.md)
- [AWS SQS queues](../../aws/containers/concepts/sqs-queues.md)
- [SQL patterns](../../sql-patterns/index.md)

## Sources

- https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resource-record-sets-choosing-alias-non-alias.html
- https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/migrate-dns-domain-in-use.html
- https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.Encryption.html
- https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html
- https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html
- https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Limits.html
- https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html
- https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html
- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html
- https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Introduction.html
- https://docs.aws.amazon.com/waf/latest/developerguide/waf-chapter.html
