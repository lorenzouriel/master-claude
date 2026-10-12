# SES: Identities, Sandbox, Bounces, Sending

> **Purpose**: What an application needs in place before and while sending email through SES
> **Confidence**: 0.95
> **MCP Validated**: 2026-10-02

## Overview

SES is Regional: identities, sandbox status, quotas, suppression lists, and SMTP credentials
are all per Region. New accounts start in the sandbox. Sending needs a verified identity and
a working bounce/complaint feedback path.

## Sandbox vs Production

| Property | Sandbox | Production |
|----------|---------|------------|
| Recipients | only verified addresses/domains or the mailbox simulator | any recipient |
| Default quotas | 200 messages / 24 h, 1 message / second | start low, raised automatically as reputation builds; request increases via Support |
| From/Source/Return-Path | must be verified | must be verified |
| Exit | request production access (console, or `aws sesv2 put-account-details --production-access-enabled --mail-type TRANSACTIONAL --website-url ... --contact-language EN`) | - |

AWS Support gives an initial response within 24 hours; verifying a domain first speeds approval.
The request asks for mail type (marketing vs transactional), website URL, up to 4 contact
addresses, and an acknowledgement that you have bounce/complaint handling.

## Identities

| Item | Detail |
|------|--------|
| Domain identity | covers all subdomains and addresses; Easy DKIM adds 3 CNAME records (2048-bit default, 1024 optional) |
| Email identity | only that address; case-sensitive; link expires in 24 h |
| Advanced sending (configuration sets, delegate sending) | the address needs its own explicit identity, not only domain inheritance |
| Per Region | same domain in two Regions = two identities and two DNS record sets |
| Limits | 10,000 identities per Region; DNS changes up to 72 h to propagate |
| Custom MAIL FROM | optional subdomain of the identity; needs an MX record, otherwise SES falls back to an amazonses.com subdomain or rejects (your choice) |

DKIM record names contain `_domainkey`; do not add a leading underscore to the token label;
some DNS hosts reject underscores and need support help. If DNS is in Route 53, SES can publish
the records for you.

## Bounces and Complaints

| Rule | Value |
|------|-------|
| Counts toward bounce rate | hard bounces to unverified domains only |
| Bounce rate | keep under 2%; review at 5%; sending may be paused at 10% |
| Complaint rate | keep under 0.1%; review at 0.1%; sending may be paused at 0.5% |
| Mandatory | you must have one feedback path (below); otherwise SES emails bounces to Return-Path |

Feedback paths (pick one; combining them can deliver duplicates):

1. Identity notifications to an SNS topic (bounces, complaints, deliveries) or email.
2. Event publishing through a configuration set to CloudWatch, Data Firehose, or SNS
   (Send, Delivery, Bounce, Complaint, Reject, ...).

Account-level suppression list is on by default for accounts created after 2019-11-25 (bounce
and complaint reasons); only hard bounces are added, Gmail sends no complaint data, and the
global suppression list can hold an address for up to 14 days. Use the mailbox simulator in
tests (not counted in metrics). Remove hard-bounced addresses immediately.

## Sending From an App

| Method | Notes |
|--------|-------|
| SESv2 `SendEmail` | Simple, Raw (MIME, attachments), or Template content; returns `MessageId` |
| SMTP interface | `email-smtp.<region>.amazonaws.com`; SMTP credentials are not IAM keys and are per Region; TLS required |

`MessageId` can be returned even if SES accepted but did not send (virus, bad template).
Handle `MessageRejected`, `SendingPausedException`, `AccountSuspendedException`,
`MailFromDomainNotVerifiedException`, `TooManyRequestsException` (throttle; back off).
Region: `email.sa-east-1.amazonaws.com` and `email-smtp.sa-east-1.amazonaws.com` exist.

## Common Mistakes

### Wrong

```text
Verify sender in us-east-1, deploy the app in sa-east-1, wonder why MessageRejected.
```

### Correct

```text
Verify the domain, request production access, and set up feedback in the same Region the SDK client uses.
```

## Related

- [ses-bounce-handling](../patterns/ses-bounce-handling.md)
- [route53-rds-scaling](route53-rds-scaling.md)

## Sources

- https://docs.aws.amazon.com/ses/latest/dg/request-production-access.html
- https://docs.aws.amazon.com/ses/latest/dg/creating-identities.html
- https://docs.aws.amazon.com/ses/latest/dg/faqs-enforcement.html
- https://docs.aws.amazon.com/ses/latest/dg/monitor-sending-activity.html
- https://docs.aws.amazon.com/ses/latest/dg/monitor-sending-activity-using-notifications.html
- https://docs.aws.amazon.com/ses/latest/dg/sending-email-suppression-list.html
- https://docs.aws.amazon.com/ses/latest/dg/send-email-api.html
- https://docs.aws.amazon.com/ses/latest/dg/send-email-smtp.html
- https://docs.aws.amazon.com/ses/latest/APIReference-V2/API_SendEmail.html
- https://docs.aws.amazon.com/general/latest/gr/ses.html
