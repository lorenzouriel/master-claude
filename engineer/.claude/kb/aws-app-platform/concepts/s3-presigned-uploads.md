# S3 Presigned Uploads

> **Purpose**: How browser-direct uploads to S3 work, what can and cannot be constrained
> **Confidence**: 0.90
> **MCP Validated**: 2026-10-02

## Overview

A presigned URL is a bearer token: whoever holds it can perform the signed operation until it
expires, using the permissions of the principal that signed it. Two upload flavors exist:
presigned PUT (single URL, signed headers) and presigned POST (form fields + policy).

## PUT vs POST

| Aspect | Presigned PUT | Presigned POST |
|--------|---------------|----------------|
| Client sends | `PUT` with body | multipart form: returned `fields` plus the file (`requests.post(url, data=fields, files=...)`) |
| Content-Type | must match the value used when signing | can be constrained by a policy condition |
| Size limit | no documented size condition in the presigned-URL docs | `content-length-range` condition in the POST policy |
| SDK call (boto3) | `generate_presigned_url("put_object", Params=...)` | `generate_presigned_post(Bucket, Key, Fields, Conditions, ExpiresIn=3600)` |
| Same key exists | replaced by the upload | replaced by the upload |

Practical rule: when a size cap or content-type allow-list matters, use presigned POST with
conditions; with PUT, re-check size and type server-side after upload (HeadObject) before use.

## Expiry and Credentials

| Signer | Maximum validity |
|--------|------------------|
| IAM user (SigV4) | 7 days |
| IAM role / STS temporary credentials | until the credentials expire, even if a longer expiry was requested |
| EC2 instance profile role | credential lifetime (typically about 6 hours) |
| S3 console | 1 minute - 12 hours |
| CLI / SDK | up to 7 days |

S3 checks expiry when the request starts; a transfer in progress is not cut off, but a resumed
transfer after expiry fails. Use short expiries (minutes) for uploads.
`s3:signatureAge` (milliseconds) in a bucket policy can deny old signatures.

## Required Setup

- Sign with SigV4, the bucket's Region, and virtual-hosted addressing (boto3 guide recommends
  `Config(signature_version="s3v4", s3={"addressing_style": "virtual"})`).
- Signer needs `s3:PutObject` on the key (and `kms:GenerateDataKey` if the bucket uses SSE-KMS).
- Browser uploads need a bucket CORS rule: the first matching `CORSRule` is used; `Origin`,
  method, and requested headers must match `AllowedOrigins`, `AllowedMethods`, `AllowedHeaders`.
- Object Lock with retention: uploads need `Content-MD5` or `x-amz-sdk-checksum-algorithm`.

## Common Mistakes

### Wrong

```text
- Long-lived URL (days) for user uploads
- Client-chosen object key (path traversal / overwrite of other users' objects)
- Trusting client-declared size or MIME without a policy or post-upload check
```

### Correct

```text
- Server picks the key (e.g. uploads/{case_id}/{uuid}), expiry of a few minutes
- POST policy conditions: Content-Type and content-length-range (boto3 `Conditions`;
  add the matching value to `Fields`, it is not added automatically)
- Treat the object as untrusted until the malware scan result is clean
```

## Related

- [s3-upload-scan-gate](../patterns/s3-upload-scan-gate.md)
- [s3-data-protection](s3-data-protection.md)
- [guardduty-malware-s3](guardduty-malware-s3.md)

## Sources

- https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html
- https://docs.aws.amazon.com/boto3/latest/guide/s3-presigned-urls.html
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/cors.html
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-managing.html
- POST policy reference https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-HTTPPOSTConstructPolicy.html
  (page body not retrievable by the fetch tool; `content-length-range` in POST policies is
  confirmed only from search summaries. boto3 `generate_presigned_post` signature and the
  Fields/Conditions rule are confirmed from botocore `signers.py` source.)
