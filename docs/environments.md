## Environments

Dev is the only environment built. Prod is designed but not deployed: the pipeline has one consumer (a Power BI report) and runs on a laptop scheduler, so a second copy of ~42M rows wouldn't change what the project shows.

### What already supports prod

- S3: separate dev and prod buckets (`national-defense-spending-<env>-381492047455-us-east-1-an`). Prod keeps noncurrent versions for 90 days instead of 30.
- `NDS_ENV` (default `dev`) picks the bucket and the AWS profile (`nds-extract-<env>`) for extract and load.
- Redshift connection values come from `.env` and are read through `env_var()` in `profiles.yml`, so a prod target is config, not code.
- Every AWS resource is tagged `Environment=dev|prod`.

### What prod would add

| Piece             | Dev (built)                                   | Prod (designed)                                                                   |
|-------------------|-----------------------------------------------|-----------------------------------------------------------------------------------|
| Extract identity  | `nds-extract-dev`                             | `nds-extract-prod`, same policy scoped to the prod bucket                         |
| Redshift          | namespace `nds-dev`, workgroup `nds-dev-wg`   | namespace `nds-prod`, workgroup `nds-prod-wg`, own security group and usage limit |
| COPY role         | `nds-redshift-copy-dev`                       | `nds-redshift-copy-prod`, read on the prod `prestaged/` prefix only               |
| Loader login      | `nds_admin`                                   | a dedicated loader user with grants on `raw_nds` only                             |
| dbt               | `dev` target                                  | `prod` target in `profiles.yml`, run with `--target prod`                         |
| Config            | `.env`                                        | `.env.prod` (gitignored), `NDS_ENV=prod`                                          |
| Scheduler         | Airflow in Docker Compose on a laptop         | MWAA or a container service                                                       |

Custom schemas are used as-is (no target prefix) because dev and prod are separate Redshift namespaces, so schema names never collide.

### Promotion

Changes are built and tested in dev first (`dbt build` plus the raw-layer checks), then run against prod with `NDS_ENV=prod` and `--target prod`. A first prod run would be a full backfill from the prod bucket.