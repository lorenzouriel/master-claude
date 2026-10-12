# EC2 Access, SSM, and IAM Least Privilege

> **Purpose**: Keyless administration, remote commands, and config/secret storage for EC2-hosted apps
> **Confidence**: 0.95
> **MCP Validated**: 2026-10-02

## Overview

Workloads on EC2 get credentials from an IAM role via an instance profile; humans and CI reach
the instance through Systems Manager (no inbound SSH). Config lives in Parameter Store; real
secrets belong in Secrets Manager.

## Instance Profile and Role

| Fact | Detail |
|------|--------|
| Instance profile | container for exactly one IAM role; an instance has one profile; many instances can share one |
| Console vs API | console auto-creates a profile named like the role; CLI/SDK create role and profile separately |
| Credentials | SDKs fetch temporary credentials from IMDS automatically; not limited by role max session duration |
| Changing permissions | replace the instance profile; removing a role from a profile can take up to 1 hour to apply |
| Managed policy for SSM | `AmazonSSMManagedInstanceCore` |
| Least privilege | start from managed policies, narrow with customer managed policies; use IAM Access Analyzer to generate a policy from CloudTrail activity |
| Avoid | long-lived IAM user access keys on servers |

## IMDSv2

IMDSv2 is session-token based (PUT for a token with TTL up to 6 hours, then GET with the
token header). Both versions are allowed by default; you can set an instance to require IMDSv2.
The token response hop limit defaults to 1; raise it when containers on the host need metadata
(practitioner note: Docker bridge networking adds a hop, so containers on the host often hit
"no credentials" errors until the hop limit is 2).

## Session Manager

- No open inbound ports, bastion, or SSH keys; access is controlled with IAM; logs to
  CloudTrail, S3, CloudWatch Logs. Sessions over port forwarding or SSH are not logged.
- Prerequisites: SSM Agent 2.3.68.0 or later, outbound HTTPS 443 to `ssm`, `ssmmessages`,
  `ec2messages` endpoints (or VPC interface endpoints), instance profile with SSM permissions.
- CLI sessions need the Session Manager plugin and AWS CLI 1.16.12+.
- Sessions run as `ssm-user` with administrative permissions unless restricted.

## Run Command (SendCommand)

| Parameter | Detail |
|-----------|--------|
| `DocumentName` | e.g. `AWS-RunShellScript` |
| `InstanceIds` | up to 50; or `Targets` (up to 5 tag key/value criteria) for fleets |
| `MaxConcurrency` / `MaxErrors` | defaults 50 / 0 (stop sending after the first error) |
| `TimeoutSeconds` | if not started within this time (min 30), it will not run |
| Output | `GetCommandInvocation` returns first 24,000 chars of stdout and 8,000 of stderr; send full output to S3 (`OutputS3BucketName`) or CloudWatch Logs |
| Status | `Pending, InProgress, Delayed, Success, Cancelled, TimedOut, Failed, Cancelling`; `ResponseCode -1` = not started |
| Consistency | API is eventually consistent: `InvocationDoesNotExist` right after send means retry |

## Parameter Store vs Secrets Manager

| Aspect | Parameter Store | Secrets Manager |
|--------|-----------------|-----------------|
| Types | String, StringList, SecureString (KMS) | secret value (up to 65,536 bytes) |
| Rotation | none | automatic, DB integrations |
| Cost | standard tier free (4 KB, 10,000/Region); advanced 8 KB, 100,000, billed, not downgradable | per secret per month + per call |
| History | keeps last 100 versions; update takes effect on next read, no validation or rollback | versions with staging labels, max 100 |
| AWS guidance | config values (endpoints, IDs) | credentials, API keys, tokens |

Avoid updating a secret more than once per 10 minutes (version quota). In ECS/Fargate,
Parameter Store values injected as env vars are resolved only at task start.

## Common Mistakes

### Wrong

```text
Put a database password in a plain String parameter and an IAM user key in the instance's .env.
```

### Correct

```text
Instance role + least-privilege policy; DB credential in Secrets Manager (or SecureString if no
rotation is needed); app reads it at startup via the role.
```

## Related

- [ssm-run-command-deploy](../patterns/ssm-run-command-deploy.md)
- [AWS Lambda IAM policies](../../aws/lambda/concepts/iam-policies.md)
- [Terraform IAM module](../../terraform/patterns/iam-module.md)

## Sources

- https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html
- https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html
- https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-prerequisites.html
- https://docs.aws.amazon.com/systems-manager/latest/APIReference/API_SendCommand.html
- https://docs.aws.amazon.com/systems-manager/latest/APIReference/API_GetCommandInvocation.html
- https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html
- https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-advanced-parameters.html
- https://docs.aws.amazon.com/secretsmanager/latest/userguide/reference_limits.html
- Practitioner note (not stated by AWS): the Docker-bridge extra hop explanation for IMDS hop limit.
