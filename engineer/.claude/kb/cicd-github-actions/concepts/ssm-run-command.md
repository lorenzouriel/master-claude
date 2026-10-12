# SSM Run Command for Deploys

> **Purpose**: Execute deploy scripts on EC2 via SSM SendCommand without SSH or open ports
> **Confidence**: 0.95
> **MCP Validated**: 2026-10-02

## Overview

`aws ssm send-command` runs a document (typically `AWS-RunShellScript`) on managed nodes.
The node needs SSM Agent and an instance profile permitting Systems Manager. The caller
(the OIDC role) needs `ssm:SendCommand` plus read access to results.

## The Concept

```bash
CMD_ID=$(aws ssm send-command \
  --document-name AWS-RunShellScript \
  --targets "Key=tag:Role,Values=app" \
  --parameters 'commands=["set -euo pipefail","cd /opt/app","./deploy.sh '"$TAG"'"]' \
  --timeout-seconds 600 \
  --comment "deploy $TAG" \
  --cloud-watch-output-config CloudWatchOutputEnabled=true,CloudWatchLogGroupName=/ssm/deploy \
  --query Command.CommandId --output text)

aws ssm wait command-executed --command-id "$CMD_ID" --instance-id "$INSTANCE_ID"
aws ssm get-command-invocation --command-id "$CMD_ID" --instance-id "$INSTANCE_ID" \
  --query '{s:Status,rc:ResponseCode,out:StandardOutputContent,err:StandardErrorContent}'
```

## Quick Reference

| Item | Fact |
|------|------|
| Targets | `--targets` (max 5 key/value pairs; tags, instance ids) or `--instance-ids` (max 50) |
| `--timeout-seconds` | min 30; if reached before the command starts, it will not run |
| `--comment` | max 100 chars |
| `--max-concurrency` / `--max-errors` | defaults `50` / `0` |
| `wait command-executed` | polls every 5 s, 20 failed checks max, exit code 255 on failure; takes `--instance-id` (one instance) |
| Status values | Pending, InProgress, Delayed, Success, Cancelled, TimedOut, Failed, Cancelling |
| Output via API | first 24,000 chars stdout, first 8,000 chars stderr; use CloudWatch/S3 output for full logs |
| `ResponseCode` | `-1` = not started / not received |
| Exit code | By default only the LAST command's exit code counts; use `set -e` or explicit checks |
| Consistency | API is eventually consistent; a fresh `get-command-invocation` can briefly fail |

## IAM (caller)

Scope `ssm:SendCommand` to the document ARN and to instances by tag with the condition key
`ssm:resourceTag/<key>`; a wrong-tag target returns `AccessDenied`. Also allow
`ssm:GetCommandInvocation` and `ssm:ListCommandInvocations` for polling.

## Common Mistakes

### Wrong

Commands without `set -e`: first `docker compose pull` fails, last command succeeds, status `Success`.

### Correct

Start the script with `set -euo pipefail` and verify health inside the script (see
[ec2-compose-ssm-deploy](../patterns/ec2-compose-ssm-deploy.md)).

## Practitioner notes (not from docs)

- Never interpolate untrusted values into `commands`; pass only validated tags (regex check
  in the workflow first).
- `wait` can fail on an invocation that has not registered yet (eventual consistency); a short
  retry loop on `get-command-invocation` is a common workaround.

## Related

- [oidc-aws-federation](oidc-aws-federation.md)
- [AWS KB](../../aws/index.md)

## Sources

- https://docs.aws.amazon.com/cli/latest/reference/ssm/send-command.html
- https://docs.aws.amazon.com/cli/latest/reference/ssm/wait/command-executed.html
- https://docs.aws.amazon.com/cli/latest/reference/ssm/get-command-invocation.html
- https://docs.aws.amazon.com/systems-manager/latest/userguide/run-command-handle-exit-status.html
- https://docs.aws.amazon.com/systems-manager/latest/userguide/run-command-setting-up.html
- https://docs.aws.amazon.com/systems-manager/latest/userguide/run-command.html
