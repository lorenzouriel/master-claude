# SES Bounce and Complaint Handling

> **Purpose**: Keep bounce/complaint rates low by suppressing bad addresses automatically
> **MCP Validated**: 2026-10-02 (rates, paths, suppression behavior, event JSON field names and CLI/API shapes checked against AWS docs and the botocore sesv2 model)

## When to Use

- Any app sending transactional email through SES (required for production access)
- You want per-message attribution (event publishing) rather than per-identity notifications

## Implementation

Setup (once, per Region):

```bash
aws sesv2 create-configuration-set --configuration-set-name app-transactional
aws sesv2 create-configuration-set-event-destination \
  --configuration-set-name app-transactional --event-destination-name to-sns \
  --event-destination '{"Enabled":true,"MatchingEventTypes":["BOUNCE","COMPLAINT"],
    "SnsDestination":{"TopicArn":"arn:aws:sns:sa-east-1:ACCOUNT:ses-feedback"}}'
aws sesv2 put-account-suppression-attributes --suppressed-reasons BOUNCE COMPLAINT
```

Send with the configuration set (or set it as the identity default):

```python
import boto3

ses = boto3.client("sesv2", region_name="sa-east-1")

def send(to: str, subject: str, html: str, text: str) -> str:
    resp = ses.send_email(
        FromEmailAddress="no-reply@example.com",         # verified identity in this Region
        Destination={"ToAddresses": [to]},
        Content={"Simple": {
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {"Html": {"Data": html, "Charset": "UTF-8"},
                     "Text": {"Data": text, "Charset": "UTF-8"}},
        }},
        ConfigurationSetName="app-transactional",
    )
    return resp["MessageId"]          # store it: it is how you map feedback to a message
```

Consume feedback (SNS -> HTTPS endpoint or SQS -> worker). Field names below follow the SES
event-publishing JSON (with identity-level notifications the top-level key is `notificationType`
instead of `eventType`); still confirm against a real mailbox-simulator event before shipping:

```python
import json

def handle_sns(body: dict) -> None:
    event = json.loads(body["Message"])                  # SNS wraps the SES event as a string
    kind = event.get("eventType")                        # "Bounce" | "Complaint"
    if kind == "Bounce" and event["bounce"]["bounceType"] == "Permanent":
        for r in event["bounce"]["bouncedRecipients"]:
            mark_undeliverable(r["emailAddress"], reason="hard_bounce")
    elif kind == "Complaint":
        for r in event["complaint"]["complainedRecipients"]:
            mark_undeliverable(r["emailAddress"], reason="complaint")
    # idempotent: SES/SNS may deliver duplicates
```

## Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| Account suppression list | `BOUNCE COMPLAINT` | default-on for accounts created after 2019-11-25; only hard bounces added |
| Targets | keep bounce < 2%, complaint < 0.1% | review at 5% / 0.1%; pause possible at 10% / 0.5% |
| Duplicate paths | use one of identity notifications or event publishing | combining yields duplicate notifications |
| Test address | SES mailbox simulator | does not count toward metrics |

## Pitfalls

- A 200 from `SendEmail` is acceptance, not delivery; SES can accept and not send (virus, bad template).
- Do not retry hard-bounced addresses; do not send a "sorry you unsubscribed" mail to complainers.
- Sandbox accounts: recipients must be verified, or use the simulator.
- CloudWatch alarms on `Reputation.BounceRate` / `Reputation.ComplaintRate` give early warning.
- Dedicated Return-Path/feedback address must exist: with no feedback path, SES mails the Return-Path address.

## See Also

- [ses-sending](../concepts/ses-sending.md)
- [AWS SQS retry and DLQ](../../aws/containers/patterns/sqs-retry-dlq.md)

## Sources

- https://docs.aws.amazon.com/ses/latest/dg/faqs-enforcement.html
- https://docs.aws.amazon.com/ses/latest/dg/monitor-sending-activity-using-notifications.html
- https://docs.aws.amazon.com/ses/latest/dg/monitor-sending-activity.html
- https://docs.aws.amazon.com/ses/latest/dg/sending-email-suppression-list.html
- https://docs.aws.amazon.com/ses/latest/APIReference-V2/API_SendEmail.html
- https://docs.aws.amazon.com/ses/latest/dg/event-publishing-retrieving-sns-contents.html
- https://docs.aws.amazon.com/ses/latest/dg/event-publishing-retrieving-sns-examples.html
- botocore `sesv2/2019-09-27/service-2.json` (EventType enum, EventDestinationDefinition, SnsDestination)
- https://docs.aws.amazon.com/ses/latest/dg/sending-email-global-suppression-list.html (global list, up to 14 days)
