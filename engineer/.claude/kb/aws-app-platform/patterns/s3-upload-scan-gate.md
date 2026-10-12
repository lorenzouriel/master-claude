# Upload, Scan, Gate: Presigned POST + GuardDuty + Tag Policy

> **Purpose**: Accept user documents directly into S3 and release them only after a clean malware verdict
> **MCP Validated**: 2026-10-02 (boto3 `generate_presigned_post` checked against botocore source; GuardDuty event/tag/policy checked against AWS docs; `get_object_tagging` is standard boto3)

## When to Use

- Users upload documents (PDF/images) from a browser
- Files must not be readable by the app (or other users) until scanned
- Bucket uses SSE-KMS and versioning

## Flow

```text
1. API authenticates user, creates DB row (status=pending), picks key uploads/{case_id}/{uuid}
2. API returns presigned POST (size + type constraints, few-minute expiry)
3. Browser POSTs file to S3 (CORS rule on the bucket)
4. GuardDuty scans the new object (POST Object triggers it) and tags it
5. Verdict arrives: EventBridge event and/or tag GuardDutyMalwareScanStatus
6. App marks row clean/infected/unscanned; bucket policy blocks reads until NO_THREATS_FOUND
```

## Implementation

```python
import boto3
from botocore.config import Config

s3 = boto3.client(
    "s3",
    region_name="sa-east-1",
    config=Config(signature_version="s3v4", s3={"addressing_style": "virtual"}),
)

MAX_BYTES = 20 * 1024 * 1024


def presign_upload(bucket: str, key: str, content_type: str) -> dict:
    return s3.generate_presigned_post(
        Bucket=bucket,
        Key=key,
        Fields={"Content-Type": content_type},          # value sent by client
        Conditions=[
            {"Content-Type": content_type},              # must be listed as a condition too
            ["content-length-range", 1, MAX_BYTES],
        ],
        ExpiresIn=300,
    )   # -> {"url": ..., "fields": {...}}


def scan_verdict(bucket: str, key: str, version_id: str | None = None) -> str:
    """Poll fallback: read the tag GuardDuty wrote (tagging must be enabled before upload)."""
    kwargs = {"Bucket": bucket, "Key": key}
    if version_id:
        kwargs["VersionId"] = version_id
    tags = s3.get_object_tagging(**kwargs)["TagSet"]
    return next((t["Value"] for t in tags if t["Key"] == "GuardDutyMalwareScanStatus"), "PENDING")


def handle_scan_event(event: dict) -> None:
    """EventBridge detail-type 'GuardDuty Malware Protection Object Scan Result'. Idempotent."""
    d = event["detail"]
    status = d["scanResultDetails"]["scanResultStatus"]
    obj = d["s3ObjectDetails"]
    mark_document(obj["bucketName"], obj["objectKey"], obj.get("versionId"),
                  clean=(status == "NO_THREATS_FOUND"), reason=status)
```

Client side (Python example): `requests.post(p["url"], data=p["fields"], files={"file": f})`.

## Bucket Policy Gate (excerpt)

```json
{
  "Sid": "NoReadUnlessClean",
  "Effect": "Deny",
  "NotPrincipal": {"AWS": ["arn:aws:iam::ACCOUNT:role/SCAN_ROLE",
                           "arn:aws:sts::ACCOUNT:assumed-role/SCAN_ROLE/GuardDutyMalwareProtection"]},
  "Action": ["s3:GetObject", "s3:GetObjectVersion"],
  "Resource": "arn:aws:s3:::BUCKET/*",
  "Condition": {"StringNotEquals": {"s3:ExistingObjectTag/GuardDutyMalwareScanStatus": "NO_THREATS_FOUND"}}
}
```

The app's role then reads objects only after a clean tag; add the second statement from the
AWS example (deny `s3:PutObjectTagging` of that key to everyone but the scan role).

## Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| Presign expiry | 300 s | upload window; role credentials cap it anyway |
| Size cap | `content-length-range` | enforced by S3 for POST |
| Tagging | enable at plan creation | tags are not added to objects uploaded earlier |
| Rescue path | treat `UNSUPPORTED`/`ACCESS_DENIED`/`FAILED` as not clean | e.g. password-protected PDFs |

## Pitfalls

- Duplicate events happen (at-least-once); key your update on `(bucket, key, versionId)`.
- SSE-KMS: scan role needs key permission; signer needs `kms:GenerateDataKey`.
- If the scan role is deleted, scans are skipped; alert on `GuardDuty Malware Protection Resource Status Warning` / `... Error` events (detail-types
  end in `Active`, `Warning` or `Error`).
- `scan_verdict` polling needs `s3:GetObjectTagging` for the reading role (the deny policy above
  does not block tag reads); prefer the EventBridge event as the primary signal.
- Never trust the client-declared MIME type beyond the policy; also sniff content before processing.

## See Also

- [guardduty-malware-s3](../concepts/guardduty-malware-s3.md)
- [s3-presigned-uploads](../concepts/s3-presigned-uploads.md)
- [s3-data-protection](../concepts/s3-data-protection.md)
- [Python error handling](../../python/patterns/error-handling.md)

## Sources

- https://docs.aws.amazon.com/boto3/latest/guide/s3-presigned-urls.html
- https://docs.aws.amazon.com/guardduty/latest/ug/how-malware-protection-for-s3-gdu-works.html
- https://docs.aws.amazon.com/guardduty/latest/ug/monitor-with-eventbridge-s3-malware-protection.html
- https://docs.aws.amazon.com/guardduty/latest/ug/tag-based-access-s3-malware-protection.html
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingKMSEncryption.html
- `generate_presigned_post(Bucket, Key, Fields, Conditions, ExpiresIn)`: botocore `signers.py` docstring
  (conditions incl. `content-length-range`; a condition needs a matching `Fields` value). Run a smoke test.
