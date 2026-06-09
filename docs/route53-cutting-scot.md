# Route53 zone — cutting.scot

Records to recreate from the DigitalOcean zone. Apex A already created.

## A (apex) — done

- Name: _(blank = apex)_
- Type: A
- Value: `159.65.94.194`
- TTL: 60

## CNAME — Postmark Return-Path (FreeAgent mailer)

- Name: `freeagent-mailer`
- Type: CNAME
- Value: `pm.mtasv.net`
- TTL: 43200

## TXT — Postmark DKIM

- Name: `20200826173112pm._domainkey`
- Type: TXT
- Value (keep the surrounding quotes):

```
"k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCNIdAPIgvr/Is7nfbyP3zKmRjxelgyeZy82SMGOdzrQLINen8s3j6suWQLfu7ZHNrb2fYEjv1vbBaUN/TicE2KHiF8p5Q05sUV9ZcEOyb9gC42Qjq2ZSwr9qmvt/+CARx+8UyiW/WytSFPbD96A97v65egYNjWelTLkU94DoJ3FQIDAQAB"
```

- TTL: 3600

## MX — Google Workspace

One record set, name blank (apex), five values:

```
1 aspmx.l.google.com
5 alt1.aspmx.l.google.com
5 alt2.aspmx.l.google.com
10 alt3.aspmx.l.google.com
10 alt4.aspmx.l.google.com
```

- TTL: 1800

## NS — skip

DigitalOcean's nameservers. Do not copy. Route53 created its own apex NS set.

## Move DNS to Route 53 — do this now

Nameservers are still all DigitalOcean, so nothing in Route 53 (including the cert validation record) is live yet. This moves them. The apex stays pointed at the droplet through the whole swap, so the site does not go down.

### Step 0 — point the Route 53 apex back at the droplet

The apex currently aliases to CloudFront, which has no cert yet. Set it to a plain A on the droplet so the site survives the nameserver swap:

```
aws route53 change-resource-record-sets --hosted-zone-id Z0719513143168SBAFM0M --change-batch '{"Changes":[{"Action":"UPSERT","ResourceRecordSet":{"Name":"cutting.scot","Type":"A","TTL":60,"ResourceRecords":[{"Value":"159.65.94.194"}]}}]}'
```

### Step A — get the 4 Route 53 nameservers

```
aws route53 get-hosted-zone --id Z0719513143168SBAFM0M --query "DelegationSet.NameServers" --output text
```

This prints four `*.awsdns-*` names. Call them NS1–NS4.

### Step B — verify Route 53 answers correctly (use NS1 from above)

Replace `NS1` with the first nameserver. Both must answer before you swap:

```
dig @ns-214.awsdns-26.com cutting.scot A +short
```

```
dig @ns-214.awsdns-26.com cutting.scot MX +short
```

Expect `159.65.94.194` for A, and the five Google MX values. If either is wrong, fix the record in Route 53 before continuing.

### Step C — swap the nameservers at 34SP

In the 34SP control panel for cutting.scot, delete the DigitalOcean nameservers and enter NS1–NS4 from Step A. Save.

### Step D — confirm delegation moved

```
dig cutting.scot NS +short
```

When this shows the `awsdns` names (not DigitalOcean), Route 53 is authoritative. Propagation is usually minutes but can take up to 48h.

### Step E — cert now issues

Re-run the wait from step 0b; it completes once delegation has propagated:

```
aws acm wait certificate-validated --certificate-arn arn:aws:acm:us-east-1:313095418189:certificate/6fa707bc-01eb-4b1d-ab8c-38be4e2d7585 --region us-east-1
```

Then continue to step 1 (CloudFront) and step 2 (apex repoint).

## Final cutover — swap the apex off the DO droplet to CloudFront

The apex `A` still points at the droplet (`159.65.94.194`). Two changes move it to CloudFront. Fill in the three IDs first.

### 0. Get the IDs

Distribution id for `d1opazmi57ejwz.cloudfront.net`:

```
aws cloudfront list-distributions --query "DistributionList.Items[?DomainName=='d1opazmi57ejwz.cloudfront.net'].Id" --output text
```

Hosted zone id for cutting.scot:

```
aws route53 list-hosted-zones-by-name --dns-name cutting.scot --query "HostedZones[0].Id" --output text
```

### 0b. Request the cert (skip if already ISSUED)

Check first — if this prints an ARN, the cert exists; jump to step 1:

```
aws acm list-certificates --region us-east-1 --query "CertificateSummaryList[?DomainName=='cutting.scot'].CertificateArn" --output text
```

Request it (us-east-1 is required for CloudFront):

```
aws acm request-certificate --domain-name cutting.scot --validation-method DNS --region us-east-1 --query CertificateArn --output text
```

Get the DNS validation CNAME:

```
aws acm describe-certificate --certificate-arn arn:aws:acm:us-east-1:313095418189:certificate/6fa707bc-01eb-4b1d-ab8c-38be4e2d7585 --region us-east-1 --query "Certificate.DomainValidationOptions[0].ResourceRecord"
```

Add that record to the hosted zone (replace `Z0719513143168SBAFM0M`):

```
aws route53 change-resource-record-sets --hosted-zone-id Z0719513143168SBAFM0M --change-batch '{"Changes":[{"Action":"UPSERT","ResourceRecordSet":{"Name":"_b12382ee4f11df8e50d21a1f7d691580.cutting.scot.","Type":"CNAME","TTL":300,"ResourceRecords":[{"Value":"_653ff77002b716fb9ae57efc137926b1.jkddzztszm.acm-validations.aws."}]}}]}'
```

Wait for issuance (blocks until validated):

```
aws acm wait certificate-validated --certificate-arn arn:aws:acm:us-east-1:313095418189:certificate/6fa707bc-01eb-4b1d-ab8c-38be4e2d7585 --region us-east-1
```

### 1. Add cutting.scot + cert to the CloudFront distribution

Dump the current config and its ETag (replace `EL227XDLWHK8L`):

```
aws cloudfront get-distribution-config --id EL227XDLWHK8L > /tmp/cf.json
```

```
ETAG=$(jq -r '.ETag' /tmp/cf.json)
```

Set the alias and the cert, writing the inner config to a new file:

```
jq --arg cert "arn:aws:acm:us-east-1:313095418189:certificate/6fa707bc-01eb-4b1d-ab8c-38be4e2d7585" '.DistributionConfig | .Aliases = {"Quantity":1,"Items":["cutting.scot"]} | .ViewerCertificate = {"ACMCertificateArn":$cert,"SSLSupportMethod":"sni-only","MinimumProtocolVersion":"TLSv1.2_2021","CloudFrontDefaultCertificate":false}' /tmp/cf.json > /tmp/cf-config.json
```

Apply it:

```
aws cloudfront update-distribution --id EL227XDLWHK8L --if-match "$ETAG" --distribution-config file:///tmp/cf-config.json
```

### 2. Repoint the Route 53 apex to CloudFront

`Z2FDTNDATAQYW2` is CloudFront's fixed alias hosted-zone id (same for every distribution). This UPSERT replaces the old droplet A record (replace `Z0719513143168SBAFM0M`):

```
aws route53 change-resource-record-sets --hosted-zone-id Z0719513143168SBAFM0M --change-batch '{"Changes":[{"Action":"UPSERT","ResourceRecordSet":{"Name":"cutting.scot","Type":"A","AliasTarget":{"HostedZoneId":"Z2FDTNDATAQYW2","DNSName":"d1opazmi57ejwz.cloudfront.net","EvaluateTargetHealth":false}}}]}'
```

### 3. Verify

```
dig cutting.scot A +short
```

```
curl -sS -o /dev/null -w '%{http_code}\n' https://cutting.scot/
```

The A answer should resolve to CloudFront, not `159.65.94.194`, and curl should print `200`. Then the droplet can be retired.

