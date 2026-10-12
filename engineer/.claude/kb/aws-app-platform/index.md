# AWS App Platform Knowledge Base

> **Purpose**: AWS services for a small web application platform (auth, email, uploads, EC2 ops, DNS, database basics); distinct from the data-engineering [aws](../aws/index.md) domain
> **MCP Validated**: 2026-10-02 (primary sources: docs.aws.amazon.com; flagged items listed in each file's Sources)

## Quick Navigation

### Concepts (< 150 lines each)

| File | Purpose |
|------|---------|
| [concepts/cognito-tokens-groups.md](concepts/cognito-tokens-groups.md) | ID vs access tokens, JWKS verification steps, groups, managed login vs hosted UI |
| [concepts/s3-presigned-uploads.md](concepts/s3-presigned-uploads.md) | Presigned PUT vs POST, expiry rules, size/type constraints, CORS |
| [concepts/s3-data-protection.md](concepts/s3-data-protection.md) | SSE-KMS, Bucket Keys, versioning, Object Lock |
| [concepts/guardduty-malware-s3.md](concepts/guardduty-malware-s3.md) | Malware scan triggers, result delivery (EventBridge/tag), quotas |
| [concepts/ses-sending.md](concepts/ses-sending.md) | Identities, sandbox exit, bounce/complaint thresholds, sending API/SMTP |
| [concepts/ssm-ec2-iam.md](concepts/ssm-ec2-iam.md) | Instance profiles, IMDSv2, Session Manager, Run Command, Parameter Store vs Secrets Manager |
| [concepts/route53-rds-scaling.md](concepts/route53-rds-scaling.md) | Alias vs CNAME, RDS encryption/Multi-AZ, when to add ALB/Fargate/SQS/CloudFront/WAF |

### Patterns (< 200 lines each)

| File | Purpose |
|------|---------|
| [patterns/cognito-jwt-verification.md](patterns/cognito-jwt-verification.md) | FastAPI dependency that verifies Cognito JWTs and enforces groups |
| [patterns/s3-upload-scan-gate.md](patterns/s3-upload-scan-gate.md) | Presigned POST upload, GuardDuty scan, tag-gated reads |
| [patterns/ses-bounce-handling.md](patterns/ses-bounce-handling.md) | Configuration set + SNS feedback, suppression, send code |
| [patterns/ssm-run-command-deploy.md](patterns/ssm-run-command-deploy.md) | CI deploy to EC2 via SendCommand with polling |

---

## Quick Reference

- [quick-reference.md](quick-reference.md) - Quotas, limits, and decision tables

---

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Token use** | Access token (`client_id`, scopes) authorizes APIs; ID token (`aud`) carries identity |
| **Presigned POST** | Only presigned form with a documented size condition (`content-length-range`) |
| **Scan verdict** | GuardDuty never deletes objects; gate reads on `GuardDutyMalwareScanStatus` |
| **SES per Region** | Identities, sandbox, SMTP credentials are Regional; use the same Region as the SDK client |
| **Instance profile** | One role per instance; apps get temporary credentials from IMDS |
| **Config vs secret** | Parameter Store for config; Secrets Manager for credentials needing rotation |

---

## Learning Path

| Level | Files |
|-------|-------|
| **Beginner** | concepts/ssm-ec2-iam.md, concepts/cognito-tokens-groups.md |
| **Intermediate** | concepts/s3-presigned-uploads.md, concepts/ses-sending.md, patterns/cognito-jwt-verification.md |
| **Advanced** | patterns/s3-upload-scan-gate.md, concepts/s3-data-protection.md, patterns/ssm-run-command-deploy.md |

---

## Cross-Domain Links

| Need | Go to |
|------|-------|
| Lambda, Glue, SAM, ECS/SQS ops | [aws](../aws/index.md) |
| Terraform for these resources | [terraform](../terraform/index.md) |
| Settings/validation models | [pydantic](../pydantic/index.md) |
| Async Python and error handling | [python](../python/index.md) |
| Testing token/AWS stubs | [testing](../testing/index.md) |
| React token handling | [javascript](../javascript/index.md) |

---

## Agent Usage

| Agent | Primary Files | Use Case |
|-------|---------------|----------|
| aws-app-platform-specialist | all concepts, patterns/s3-upload-scan-gate.md, patterns/ssm-run-command-deploy.md | Design and review AWS resources, IAM scopes, regional constraints |
| fastapi-backend-specialist | patterns/cognito-jwt-verification.md, patterns/ses-bounce-handling.md, concepts/s3-presigned-uploads.md | Auth dependency, email sending, upload endpoints |
| react-frontend-specialist | concepts/cognito-tokens-groups.md, concepts/s3-presigned-uploads.md | Token types in the SPA, direct-to-S3 upload with presigned POST and CORS |

## Known Gaps

- Malware Protection for S3 availability in `sa-east-1` and RDS availability in `sa-east-1` were not confirmed on docs.aws.amazon.com.
- S3 POST policy reference page and SES event-publishing JSON page could not be rendered by the fetch tool; related claims are marked in file Sources.
