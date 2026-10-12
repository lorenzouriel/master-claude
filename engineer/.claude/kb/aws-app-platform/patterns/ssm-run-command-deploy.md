# Deploy via SSM Run Command

> **Purpose**: Roll out a new container version to an EC2 host from CI without SSH or inbound ports
> **MCP Validated**: 2026-10-02 (SendCommand/GetCommandInvocation fields and IAM action names verified; shell script is illustrative)

## When to Use

- CI (for example GitHub Actions) must run a deploy script on one or a few instances
- The instance has an instance profile with SSM permissions and the SSM Agent running
- No SSH access is exposed

## Implementation

```python
import time

import boto3

ssm = boto3.client("ssm", region_name="sa-east-1")

DEPLOY_SCRIPT = [
    "set -euo pipefail",
    "cd /opt/app",
    "docker compose pull",
    "docker compose up -d --remove-orphans",
    "docker compose ps",
]


def deploy(instance_id: str, bucket: str, timeout_s: int = 600) -> str:
    sent = ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={"commands": DEPLOY_SCRIPT},       # parameter name defined by the document
        Comment="app deploy",                          # max 100 chars
        TimeoutSeconds=60,                             # delivery timeout, min 30
        OutputS3BucketName=bucket,                     # full output beyond 24k chars
        OutputS3KeyPrefix="ssm-deploy/",
        MaxErrors="0",
    )
    command_id = sent["Command"]["CommandId"]

    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            inv = ssm.get_command_invocation(CommandId=command_id, InstanceId=instance_id)
        except ssm.exceptions.InvocationDoesNotExist:   # eventual consistency right after send
            time.sleep(2)
            continue
        if inv["Status"] in {"Success", "Failed", "Cancelled", "TimedOut"}:
            if inv["Status"] != "Success":
                raise RuntimeError(f"deploy {inv['Status']}: {inv['StandardErrorContent']}")
            return inv["StandardOutputContent"]
        time.sleep(3)
    raise TimeoutError(command_id)
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `InstanceIds` | - | up to 50 IDs; use `Targets=[{"Key":"tag:Role","Values":["app"]}]` for fleets (max 5 criteria) |
| `MaxConcurrency` | `50` | instances running at once; use `1` or `25%` for rolling deploys |
| `MaxErrors` | `0` | stop dispatching after the first error beyond this count |
| `TimeoutSeconds` | - | command not started within this time will not run (30 - 2,592,000) |
| stdout / stderr in API | 24,000 / 8,000 chars | send to S3 or CloudWatch Logs for everything else |

## Secrets

Do not put secrets in `commands` (they appear in command history). Have the host read them at
run time from Parameter Store/Secrets Manager using its instance role, for example
`aws ssm get-parameter --with-decryption --name /app/prod/DB_URL` inside the script.

## IAM (least privilege sketch)

- CI role: `ssm:SendCommand` on the target instance ARNs and the `AWS-RunShellScript` document,
  `ssm:GetCommandInvocation`, `ssm:ListCommandInvocations`; scope by instance tag with a condition.
- Instance role: `AmazonSSMManagedInstanceCore` plus read on its own parameter path and ECR/registry pull access.
- Prefer short-lived CI credentials (OIDC federation) over stored IAM user keys.

## Pitfalls

- `Success` means the script exited 0; add health checks (`curl` the app) inside the script.
- `docker compose up -d` with `set -e` and a failed health check leaves the new version running; keep the previous tag to roll back.
- Eventual consistency: do not treat the first `InvocationDoesNotExist` as failure.
- Command status `Delayed` means the node was unreachable; the system retries until timeout.

## See Also

- [ssm-ec2-iam](../concepts/ssm-ec2-iam.md)
- [AWS GitHub Actions CI](../../aws/containers/patterns/github-actions-ci.md)
- [Terraform remote state](../../terraform/patterns/remote-state.md)

## Sources

- https://docs.aws.amazon.com/systems-manager/latest/APIReference/API_SendCommand.html
- https://docs.aws.amazon.com/systems-manager/latest/APIReference/API_GetCommandInvocation.html
- https://docs.aws.amazon.com/systems-manager/latest/userguide/run-command.html
- https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- https://docs.aws.amazon.com/systems-manager/latest/userguide/documents-command-ssm-plugin-reference.html
  (`commands` parameter of the aws:runShellScript document)
- AWS Service Reference (servicereference.us-east-1.amazonaws.com): `ssm:SendCommand`,
  `ssm:GetCommandInvocation`, `ssm:ListCommandInvocations` exist; SendCommand resource types are
  document, instance, managed-instance, bucket; condition key `ssm:resourceTag/${TagKey}`.
- Practitioner note: scoping the CI role to those resources and OIDC federation advice are general
  AWS practice, not stated on the pages above.
