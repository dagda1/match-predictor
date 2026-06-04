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

## Verify before swapping nameservers

Query Route53 directly (replace `ns-XXX...` with one of the four nameservers shown in the hosted zone's NS record). Mail and apex must answer correctly here before the registrar swap:

```
dig @ns-XXX.awsdns-XX.com cutting.scot A +short
dig @ns-XXX.awsdns-XX.com cutting.scot MX +short
```

Expect `159.65.94.194` for A, and the five Google MX values.

## Nameserver swap (34SP) — only after verify passes

In the 34SP control panel, replace the DigitalOcean nameservers with the four Route53 ones from the hosted zone's NS record. Then:

```
dig +trace cutting.scot NS
```

Expect the delegation to point at `awsdns` nameservers (can take 24–48h to propagate).

