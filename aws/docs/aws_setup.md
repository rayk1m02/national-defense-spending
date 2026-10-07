# AWS Setup

Region: us-east-1. All resources tagged `Project=national-defense-spending` and `Environment=<dev|prod>`.

## S3 Buckets

| Setting                             | Dev                                                       | Prod                                                       |
|-------------------------------------|-----------------------------------------------------------|------------------------------------------------------------|
| Name                                | `national-defense-spending-dev-381492047455-us-east-1-an` | `national-defense-spending-prod-381492047455-us-east-1-an` |
| Namespace                           | Account regional                                          | Account regional                                           |
| Versioning                          | Enabled                                                   | Enabled                                                    |
| Block Public Access                 | All on                                                    | All on                                                     |
| Encryption                          | SSE-S3, Bucket Key on                                     | SSE-S3, Bucket Key on                                      |
| Noncurrent version expiry           | 30 days                                                   | 90 days                                                    |
| Incomplete multipart upload cleanup | 7 days                                                    | 7 days                                                     |

### Prefixes

- `raw/`: bulk files exactly as downloaded, never modified
- `prestaged/`: filtered, column-trimmed CSVs for Redshift `COPY`

```
raw/<source>/full/fiscal_year=<YYYY>/
raw/<source>/delta/load_date=<YYYY-MM-DD>/ # USASpending generation date (updated_date)
```
`prestaged/` mirrors the same layout. DHS has no Delta files so far

### Verification commands

```bash
aws s3api get-bucket-versioning --bucket <bucket> --no-cli-pager
aws s3api get-public-access-block --bucket <bucket> --no-cli-pager
aws s3api get-bucket-encryption --bucket <bucket> --no-cli-pager
aws s3api get-bucket-tagging --bucket <bucket> --no-cli-pager
aws s3api get-bucket-lifecycle-configuration --bucket <bucket> --no-cli-pager
```

## IAM

`nds-extract-dev` user, policy `nds-extract-dev-policy` (`aws/iam/extract-dev-policy.json`):
- `s3:PutObject`, `s3:AbortMultipartUpload` on `raw/*` and `prestaged/*` (dev bucket)
- `s3:ListBucket` limited to those two prefixes
- No `GetObject`, no `DeleteObject`, no prod access

Policy versions: v1 (2026-10-02, `raw/` only), v2 (2026-10-03, added `prestaged/`).

```bash
aws iam list-policy-versions --policy-arn arn:aws:iam::381492047455:policy/nds-extract-dev-policy --no-cli-pager
```

`nds-redshift-copy-dev` role, assumed by Redshift, policy `nds-redshift-copy-dev-policy` (`aws/iam/redshift-copy-dev-policy.json`):
- `s3:GetObject` on `prestaged/*` (dev bucket)
- `s3:ListBucket` limited to `prestaged/*`
- No write access, no `raw/`, no prod

## Redshift Serverless

| Setting               | Value                                                     |
|-----------------------|-----------------------------------------------------------|
| Namespace             | `nds-dev`                                                 |
| Workgroup             | `nds-dev-wg`                                              |
| Database              | `nds`                                                     |
| Admin user            | `nds_admin` (password in AWS Secret Manager)              |
| Base capacity         | 4 RPU                                                     |
| Usage limit           | 40 RPU-hours monthly, turn off user queries               |
| Encryption            | AWS-owned key                                             |
| Enhanced VPC routing  | Off                                                       |
| Publicly accessible   | On                                                        |
| Security group        | `nds-redshift-dev-sg`: inbound TCP 5439 from my IP only   |
| Default IAM role      | `nds-redshift-copy-dev`                                   |

Endpoint: `nds-dev-wg.381492047455.us-east-1.redshift-serverless.amazonaws.com:5439`

If my IP changes, update the inbound rule on `nds-redshift-dev-sg`.