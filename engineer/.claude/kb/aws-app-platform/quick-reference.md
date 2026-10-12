# AWS App Platform Quick Reference

> Fast lookup tables. For code examples, see linked files. Verified 2026-10-02 against docs.aws.amazon.com.

## Cognito

| Item | Value |
|------|-------|
| Signing | RS256; separate keys for ID and access tokens |
| JWKS | `https://cognito-idp.{region}.amazonaws.com/{poolId}/.well-known/jwks.json` |
| Issuer | `https://cognito-idp.{region}.amazonaws.com/{poolId}` |
| ID token check | `aud` = app client, `token_use=id` |
| Access token check | `client_id` = app client, `token_use=access`; no `aud` by default |
| Token lifetimes | ID/access 5 min - 1 day; refresh 1 h - 3,650 days |
| Groups | `cognito:groups`; 10,000/pool, 100/user, no nesting |

## Limits and Quotas

| Service | Limit | Value |
|---------|-------|-------|
| S3 presigned | IAM user URL max | 7 days (SDK/CLI); console 1 min - 12 h |
| S3 presigned | role credentials | URL dies with the session |
| S3 Object Lock | max retention | 100 years |
| GuardDuty S3 scan | max object / protected buckets | 100 GB / 25 per Region |
| SES sandbox | send quota | 200 per 24 h, 1 per second |
| SES | identities per Region | 10,000 |
| SES rates | bounce review / pause | 5% / 10% (keep < 2%) |
| SES rates | complaint review / pause | 0.1% / 0.5% (keep < 0.1%) |
| SSM SendCommand | InstanceIds / Targets | 50 / 5 criteria |
| SSM GetCommandInvocation | stdout / stderr | 24,000 / 8,000 chars |
| Parameter Store | standard / advanced value | 4 KB (10,000) / 8 KB (100,000) |
| Secrets Manager | value size / secrets per Region | 65,536 bytes / 500,000 |
| RDS | DB instances default | 40 per Region |

## Region Notes (sa-east-1, Sao Paulo)

| Service | Status |
|---------|--------|
| Cognito user pools | listed |
| SES (API + SMTP + inbound) | listed (`email.sa-east-1.amazonaws.com`) |
| GuardDuty service | listed |
| GuardDuty Malware Protection for S3 | available (AWS announcement: all GuardDuty Regions except China/GovCloud) |
| RDS | not verified here |

## Decision Matrix

| Use Case | Choose |
|----------|--------|
| Cap upload size/type at S3 | Presigned POST with `content-length-range` |
| Keep unscanned files unreadable | Bucket policy on `GuardDutyMalwareScanStatus` tag |
| Admin shell on EC2, no SSH | Session Manager |
| Run deploy script from CI | SSM `SendCommand` + `GetCommandInvocation` |
| App config values | Parameter Store (String/SecureString) |
| DB credentials needing rotation | Secrets Manager |
| Root domain to load balancer/CDN | Route 53 alias record |
| Block public web abuse | AWS WAF on ALB or CloudFront |
| Durable async work beyond the DB queue | SQS |

## Common Pitfalls

| Don't | Do |
|-------|-----|
| Verify access token with `aud` check | Check `client_id` and `token_use` |
| Rely on offline JWT check for sign-out | Short access tokens or ask Cognito |
| Enable Object Lock Compliance to experiment | Test in Governance mode first |
| Send encryption headers on GET of SSE-KMS object | Omit them (HTTP 400) |
| Assume `SendEmail` 200 means delivered | Handle bounce/complaint events |
| Put secrets in SendCommand `commands` | Read from Parameter Store/Secrets Manager on host |
| Add CNAME at zone apex | Use alias/A record |
| Plan to encrypt RDS later | Enable at creation (snapshot-copy otherwise) |

## Related Documentation

| Topic | Path |
|-------|------|
| Full Index | `index.md` |
| Auth | `concepts/cognito-tokens-groups.md` |
| Uploads | `concepts/s3-presigned-uploads.md` |
| Email | `concepts/ses-sending.md` |
| EC2/SSM | `concepts/ssm-ec2-iam.md` |
