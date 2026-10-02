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

### Verification commands

```bash
aws s3api get-bucket-versioning --bucket <bucket> --no-cli-pager
aws s3api get-public-access-block --bucket <bucket> --no-cli-pager
aws s3api get-bucket-encryption --bucket <bucket> --no-cli-pager
aws s3api get-bucket-tagging --bucket <bucket> --no-cli-pager
aws s3api get-bucket-lifecycle-configuration --bucket <bucket> --no-cli-pager
```