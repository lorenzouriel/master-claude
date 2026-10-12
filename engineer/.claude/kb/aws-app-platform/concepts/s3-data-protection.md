# S3 Data Protection: SSE-KMS, Versioning, Object Lock

> **Purpose**: Encryption at rest, accidental-delete recovery, and WORM retention for S3 buckets
> **Confidence**: 0.95
> **MCP Validated**: 2026-10-02

## Overview

Every new S3 object is encrypted at rest with SSE-S3 by default (since 2023-01-05). SSE-KMS adds
key policy control and CloudTrail auditing of key use. Versioning keeps prior versions after
overwrite or delete. Object Lock adds retention on top of versioning.

## Layers

| Control | What it gives | Cost / catch |
|---------|---------------|--------------|
| SSE-S3 (default) | encryption at rest, no setup | no per-key access control or audit |
| SSE-KMS | key policy, rotation control, CloudTrail `GenerateDataKey`/`Decrypt` events | KMS request cost; extra permissions; same-Region key |
| S3 Bucket Key | cuts KMS request cost by up to 99% | encryption context becomes the bucket ARN, not object ARN |
| Versioning | recover from overwrite/delete (delete creates a delete marker) | each version is billed as a full object |
| Object Lock | WORM: retention period and/or legal hold per object version | requires versioning; cannot be turned off afterward |

## SSE-KMS Rules

- Symmetric encryption KMS keys only; key must be in the same Region as the bucket.
- Upload needs `kms:GenerateDataKey`; download needs `kms:Decrypt`; multipart needs both.
- Principals that sign presigned URLs need these permissions too.
- Do not send encryption headers on GET/HEAD for SSE-KMS objects (HTTP 400).
- `aws/s3` AWS managed key objects cannot be shared cross-account; use a customer managed key.
- If a customer managed key is disabled or deleted, objects become unreadable; Object Lock does
  not protect against key loss.
- Enforce at policy level: deny `s3:PutObject` when
  `s3:x-amz-server-side-encryption-aws-kms-key-id` is null; use full key ARNs, not aliases,
  for cross-account cases.
- If IAM or key policies key off the object ARN encryption context, they break when Bucket Keys
  are enabled; switch them to the bucket ARN first. Existing objects do not use the Bucket Key
  until copied.

## Versioning

States: unversioned (default), enabled, suspended. Once enabled, a bucket can never return to
unversioned. Pair with a noncurrent-version expiration lifecycle rule or storage grows without
bound. Existing objects keep version ID `null` until modified.

## Object Lock

| Item | Detail |
|------|--------|
| Modes | Governance (bypass with `s3:BypassGovernanceRetention` + header) and Compliance (nobody, including root, can shorten or delete) |
| Legal hold | no expiry; needs `s3:PutObjectLegalHold` to set/remove |
| Scope | protects the specific object version only; new versions and delete markers still happen |
| Irreversible | cannot disable Object Lock or suspend versioning on the bucket afterward |
| Upload requirement | retention uploads need `Content-MD5` or `x-amz-sdk-checksum-algorithm` |
| Max retention | 100 years |
| Compliance mode warning | only deleting the AWS account removes data before expiry; test with Governance first |

## Common Mistakes

### Wrong

```text
Enable Compliance-mode default retention on a production bucket to "try it out".
```

### Correct

```text
Prototype in Governance mode in a throwaway bucket; confirm lifecycle and delete-marker
behavior; only then choose Compliance and a retention period you can live with.
```

## Related

- [s3-presigned-uploads](s3-presigned-uploads.md)
- [guardduty-malware-s3](guardduty-malware-s3.md)
- [AWS S3 operations (data engineering)](../../aws/deployment/patterns/s3-operations.md)

## Sources

- https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingKMSEncryption.html
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-encryption.html
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-key.html
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-managing.html
