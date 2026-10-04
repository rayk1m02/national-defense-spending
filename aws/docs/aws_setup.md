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
`prestaged/` mirrors the same layout. DHS has no Delta files.

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